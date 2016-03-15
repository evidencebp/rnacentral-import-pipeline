"""
Copyright [2009-2014] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Usage:

python path/to/this/file.py
    --local-scheduler
    --destination /path/to/output/files
    --input-file /path/to/input/file.json

Optional parameters:
    --test # to process just the first few entries (default: False)
"""

import luigi

from rnacentral_entry import RNAcentralEntry
from json_parser import JsonParser


class JsonParserNoncode(JsonParser):  # pylint: disable=W0232
    """
    Luigi Task for converting Noncode Json file into csv files
    that can be loaded into the RNAcentral database.
    """
    database = 'noncode'

    def get_accession(self, entry, database):
        """
        Get Noncode unique accession.
        """
        return entry.primary_id # use transcript id as a

    def create_rnacentral_entries(self):
        """
        Process json file into RNAcentralEntry objects that can be written
        to the output files using standard methods.
        """
        for i, seq in enumerate(self.data): # pylint: disable=E1101
            if self.test and i > 100: # pylint: disable=E1101
                break

            (feature_location_start, feature_location_end) = self.get_feature_start_end(seq['assembly_info']) # pylint: disable=E1101

            rnacentral_entry = RNAcentralEntry(
                chromosome = seq['chromosome'],
                common_name = seq['common_name'],
                database = self.database.upper(),
                division='XXX', # pylint: disable=W0511
                feature_location_end=feature_location_end,
                feature_location_start=feature_location_start,
                feature_type = seq['feature_type'],
                gene = seq['gene_id'],
                is_composite = 'N',
                lineage='; '.join(seq['lineage'] + [seq['scientific_name']]),
                ncbi_tax_id = seq['ncbi_tax_id'],
                ncrna_class = seq['ncrna_class'],
                note = ' '.join(seq['ontology']),
                optional_id = seq['gene_id'],
                parent_accession = seq['primary_accession'].split('.')[0],
                primary_id = seq['transcript_id'],
                product = seq['product'],
                project = 'PRJ_NNCD',
                sequence = seq['sequence'].upper(),
                seq_version = seq['primary_accession'].split('.')[1] if '.' in seq['primary_accession'] else '1',
                species = seq['scientific_name'],
                references=[
                    {
                        'authors': 'Zhao Y, Li H, Fang S, Kang Y, Wu W, Hao Y, Li Z, Bu D4, Sun N, Zhang MQ, Chen R',
                        'location': 'Nucleic Acids Res. 2016 Jan 4;44(D1):D203-8',
                        'title': 'NONCODE 2016: an informative and valuable data source of long non-coding RNAs',
                        'pmid': 26586799,
                        'doi': '10.1093/nar/gkv1252',
                    }
                ],
            )

            if 'Unknown' in rnacentral_entry.parent_accession:
                print 'Skipping an entry with an Unknown primary accession'
                continue

            for exon in seq['assembly_info']:
                rnacentral_entry.assembly_info.append(exon)
            rnacentral_entry.accession = self.get_accession(rnacentral_entry, self.database) # pylint: disable=E1101
            rnacentral_entry.description = self.get_description(rnacentral_entry) # pylint: disable=E1101
            self.entries.append(rnacentral_entry) # pylint: disable=E1101


# main entry point
if __name__ == '__main__':
    luigi.run(main_task_cls=JsonParserNoncode)