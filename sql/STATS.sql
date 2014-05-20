-- Copyright [2009-2014] EMBL-European Bioinformatics Institute
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--      http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

set define off

create or replace package stats
is

   /**
    * Counts the number of UPIs that were active in a given
    * moment of time especified by a release id.
    */
function get_total_active_upi (in_release_id IN PLS_INTEGER)
    return PLS_INTEGER;

function get_active_xref (in_release_id IN PLS_INTEGER)
    return PLS_INTEGER;


function get_db_xref (in_dbid IN PLS_INTEGER)
    return PLS_INTEGER;

end stats;
/
create or replace package body stats

is

   function get_total_active_upi (in_release_id IN PLS_INTEGER)
     return PLS_INTEGER

   is


   v_total_active PLS_INTEGER;

   begin

     select count(unique(upi))
     into v_total_active
     from xref a
     where created <= in_release_id
     and last >= (select max(id) from rnc_release b
                  where b.dbid = a.dbid and b.id <= in_release_id
                  and release_type = 'F');


     return v_total_active;

   end get_total_active_upi;


   function get_active_xref (in_release_id IN PLS_INTEGER)
     return PLS_INTEGER

   is

   v_active_xref PLS_INTEGER;

   begin


     select count (*)
     into v_active_xref
     from xref
     where created <= in_release_id
     and deleted = 'N';

   return v_active_xref;

  end get_active_xref;

  function get_db_xref (in_dbid IN PLS_INTEGER)
    return PLS_INTEGER


  is

  v_db_xref PLS_INTEGER;

  begin

    select count (*)
    into v_db_xref
    from xref
    where dbid = in_dbid
    and deleted = 'N';


  return v_db_xref;

  end get_db_xref;

end stats;
/
set define on