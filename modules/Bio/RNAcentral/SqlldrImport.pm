#!/usr/bin/env perl

package Bio::RNAcentral::SqlldrImport;

=pod

=head1 NAME

    Bio::RNAcentral::SqlldrImport

=head1 DESCRIPTION

    Short sequences can be loaded very fast using direct path loading.
    Long sequences are stored as CLOBs in the Oracle database
    and cannot be loaded using direct path sqlldr strategy.
    As a result, long and short sequences are loaded separately.

    Create sqlldr temporary output files (sqlldr control files and sqlldr log files)
    in the temporary directory, clean up on exit.

=cut

use strict;
use warnings;

use base ('Bio::RNAcentral::Base');


sub new {
    my ($class, $opt) = @_;

    # run parent constructor
    my $self = $class->SUPER::new();

    $self->{'job_id'}   = '';
    $self->{'seq_type'} = '';

    $self->{'user'}     = $opt->{'user'};
    $self->{'password'} = $opt->{'password'};
    $self->{'sid'}      = $opt->{'sid'};
    $self->{'port'}     = $opt->{'port'};
    $self->{'host'}     = $opt->{'host'};

    # location of temporary output files
    if ( defined($opt->{'out'}) ) {
        $self->{'opt'}{'temp_dir'} = $opt->{'out'};
    }

    return $self;
}


sub _set_filenames {
    my $self = shift;

    $self->{'ctlfile'}   = $self->get_output_filename($self->{'job_id'}, $self->{'seq_type'}, 'ctl');
    $self->{'logfile'}   = $self->get_output_filename($self->{'job_id'}, $self->{'seq_type'}, 'log');
    $self->{'csvfile'}   = $self->get_output_filename($self->{'job_id'}, $self->{'seq_type'}, 'csv');
    $self->{'badfile'}   = $self->get_output_filename($self->{'job_id'}, $self->{'seq_type'}, 'bad');
    $self->{'longfile'}  = $self->get_output_filename($self->{'job_id'}, $self->{'seq_type'}, 'long');
    $self->{'shortfile'} = $self->get_output_filename($self->{'job_id'}, $self->{'seq_type'}, 'short');
}


=head2 load_seq

    Input: location of csv file with sequence data.
    Create control files for sqlldr, launch sqlldr, report mistakes.

=cut

sub load_seq {
    (my $self, my $file) = @_;

    # get file name without extension
    $file = File::Basename::fileparse($file, qr/\.[^.]*/);

    if ( $file =~ /(.*)_(long|short)/ ) {
        $self->{'job_id'}   = $1;
        $self->{'seq_type'} = $2;
        $self->_set_filenames(); # initialize all filenames for this job_id
    } else {
        $self->{'logger'}->logwarn("Unexpected file $file");
        return;
    }

    # create sqlldr control file
    $self->_make_ctl_file();

    $self->_delete_old_log_files();

    # launch sqlldr
    my $cmd = $self->_get_sqlldr_command();
    my $problems = $self->_run_sqlldr($cmd);

    unless ( $self->_errors_found() or $problems ) {
        $self->_clean_up_files();
    }
}


=head2 _get_sqlldr_command

    Construct the sqlldr system command.

=cut

sub _get_sqlldr_command {
    my $self = shift;

    my $command = 'sqlldr ' .
                   $self->{'user'} . '/' . $self->{'password'} . '@' .
                  '\"\(DESCRIPTION=\(ADDRESS=\(PROTOCOL=TCP\)' .
                  '\(HOST=' . $self->{'host'} . '\)' .
                  '\(PORT=' . $self->{'port'} . '\)\)' .
                  '\(CONNECT_DATA\=\(SERVICE_NAME=' . $self->{'sid'} . '\)\)\)\" ' .
                  'control=' . $self->{'ctlfile'} . ' ' .
                  'bad='     . $self->{'badfile'} . ' ' .
                  'log='     . $self->{'logfile'};

    # conventional loading for lob files, direct loading for short sequences
    if ( $self->{'seq_type'} eq 'short' ) {
        $command .= ' direct=true parallel=true';
    }

    return $command;
}


=head2 _delete_old_log_files

    Delete any .bad and .log files left from previous runs.
    If they are not deleted, it may look as if the current run has an error too.

=cut

sub _delete_old_log_files {
    my $self = shift;

    my @to_delete = ($self->{'badfile'}, $self->{'logfile'});
    foreach my $file ( @to_delete ) {
        if ( -e $file ) {
            unlink $file or $self->{'logger'}->logwarn("Could not unlink $file: $!");
        }
    }
}

=head2

    Launch sqlldr and make sure that it runs successfully, log any errors.

=cut

sub _run_sqlldr {
    (my $self, my $command) = @_;
    $self->{'logger'}->info('Launching sqlldr');

    my $status = system($command); # 0 on success
    print "Status $status\n";
    unless ( $status == 0 ) {
        $self->{'logger'}->logwarn("Couldn't launch sqlldr\n. Command: $command\n Error: $!\n");
    }

    return $status;
}


=head2

    Create a control file used by sqlldr.

=cut

sub _make_ctl_file {
    my $self = shift;

    open my $fh, '>', $self->{'ctlfile'} or die $!;

    print $fh <<CTL;
LOAD DATA
INFILE '$self->{"csvfile"}' "str '\\n'"
APPEND
INTO TABLE $self->{'opt'}{'staging_table'}
FIELDS TERMINATED BY ','
(
  CRC64 char,
  LEN integer external,
CTL

    # different handling of long and short sequences
    if ( $self->{'seq_type'} eq 'short' ) {
        print $fh "  SEQ_SHORT char(" . $self->{'opt'}{'MAXSEQSHORT'} . "),\n";
    } elsif ( $self->{'seq_type'} eq 'long' ) {
        print $fh "  SEQ_LONG char("  . $self->{'opt'}{'MAXSEQLONG'}  . "),\n";
    } else {
        $self->{'logger'}->logdie("Wrong sequence sequence type");
    }

    print $fh <<CTL;
  AC char,
  VERSION integer external,
  TAXID integer external,
  MD5 char
)
CTL
    close $fh;
}


=head2 _errors_found

    Entries rejected by the database are stored in the .bad file.
    Warn if bad file exists.
    Discard file is not specified in control files, so it's never created.

=cut

sub _errors_found {
    my $self = shift;

    # TODO: find error messages in the log file

    if (-e $self->{'badfile'}) {
        $self->{'logger'}->logwarn("sqlldr import had errors, check $self->{'badfile'}");
        return 1;
    } else {
        $self->{'logger'}->info("No bad file");
        return 0;
    }
}


=head2 _clean_up_files

    Remove files the upload to save disk space.

=cut

sub _clean_up_files {
    my $self = shift;

    $self->{'logger'}->info("Cleaning up $self->{'job_id'}_$self->{'seq_type'} files");

    # no need to unlink bad file because this sub only runs when bad file doesn't exist
    unlink $self->{'ctlfile'},
           $self->{'logfile'},
           $self->{'shortfile'},
           $self->{'csvfile'},
           $self->{'longfile'};
}


1;