#!/usr/bin/env perl

package Bio::RNAcentral::OracleUpdate;

=pod

=head1 NAME

    Bio::RNAcentral::OracleUpdate

=head1 DESCRIPTION

    Manage connection to the Oracle database
    Truncate staging table in the beginning of the update
    Create new release
    Launch PL/SQL update

=cut

use strict;
use warnings;

use DBI;
use DBD::Oracle;

use base ('Bio::RNAcentral::Base');


sub new {
    my ($class, $opt) = @_;

    # run parent constructor
    my $self = $class->SUPER::new();

    $self->{'user'}     = $opt->{'user'};
    $self->{'password'} = $opt->{'password'};
    $self->{'sid'}      = $opt->{'sid'};
    $self->{'port'}     = $opt->{'port'};
    $self->{'host'}     = $opt->{'host'};

    $self->db_oracle_connect();

    return $self;
}


=head2 db_oracle_connect

    Establish a database connection and keep it open.

=cut

sub db_oracle_connect {
    my $self = shift;

    my $dsn = "dbi:Oracle:host=$self->{'host'};sid=$self->{'sid'};port=$self->{'port'}";
    my $dbh = DBI->connect($dsn, $self->{'user'}, $self->{'password'})
              or $self->{'logger'}->logdie( $DBI::errstr . "\n" );

    $self->{'dbh'} = $dbh;
    $self->{'logger'}->info("Connected to the database");
}

=head2 db_oracle_disconnect

    Close database connection.

=cut

sub db_oracle_disconnect {
    my $self = shift;

    if ( exists $self->{'dbh'} ) {
        $self->{'dbh'}->disconnect();
        $self->{'logger'}->info("Disconnected from the database");
    }
}


=head2 truncate_staging_table

    The staging table should be empty at the beginning of the import.

=cut

sub truncate_staging_table {
    my $self = shift;

    my $command = "TRUNCATE TABLE $self->{'opt'}{'staging_table'}";
    $self->{'dbh'}->do($command)
        or $self->{'logger'}->logdie("Couldn't truncate the staging table");

    $self->{'logger'}->info("Staging table truncated");
}


=head2 create_new_release

    TODO: figure out how many staging tables are going to be used.
    TODO: replace placeholder parameters with real dates etc.

=cut

sub create_new_release {
    my $self = shift;

    my $command = <<SQL;
INSERT INTO $self->{'opt'}{'release_table'}
VALUES(
  (SELECT count(*)+1 FROM rnc_release),
  1,
  '12-JUL-13',
  'F',
  'L',
  '12-JUL-13',
  'perl',
  'test',
  'N'
)
SQL

    $self->{'dbh'}->do($command)
        or $self->{'logger'}->logdie("Couldn't create new release");

    $self->{'logger'}->info("New release created");
}


=head2 run_pl_sql_update

    Update Oracle database, import sequences, create new xrefs.

=cut

sub run_pl_sql_update {
    my $self = shift;

    $self->{'logger'}->info("Launching PL/SQL update");

    my $command = <<PLSQL;
BEGIN
  RNC_UPDATE.NEW_UPDATE();
END;
PLSQL

    $self->{'dbh'}->do($command)
        or $self->{'logger'}->logdie("PL/SQL update failed");

    $self->{'logger'}->info("PL/SQL update complete");
}


1;