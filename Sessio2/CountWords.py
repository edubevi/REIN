"""
.. module:: CountWords

CountWords
*************

:Description: CountWords

    Generates a list with the counts and the words in the 'text' field of the documents in an index

:Version: 

:Date:  5/06/2018

"""

from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError, TransportError

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--alpha', action='store_true', default=False, help='Sort words alphabetically')
    args = parser.parse_args()

    index = args.index

    try:
        client = Elasticsearch()
        voc = {}
        sc = scan(client, index=index, doc_type='document', query={"query" : {"match_all": {}}})
        for s in sc:
            try:
                tv = client.termvectors(index=index, doc_type='document', id=s['_id'], fields=['text'])
                if 'text' in tv['term_vectors']:
                    for t in tv['term_vectors']['text']['terms']:
                        if t in voc:
                            voc[t] += tv['term_vectors']['text']['terms'][t]['term_freq']
                        else:
                            voc[t] = tv['term_vectors']['text']['terms'][t]['term_freq']
            except TransportError:
                pass

        lpal = []

        for v in voc:
            lpal.append((v.encode("utf8", "ignore"), voc[v]))
        
        totalOcc = 0
        for pal, cnt in sorted(lpal, key=lambda x: x[0 if args.alpha else 1]):
            print('%d, %s' % (cnt, pal.decode("utf-8")))
            totalOcc += cnt
        print('%s Distinct words, %s Word occurrences' % (len(lpal), totalOcc))
    except NotFoundError:
        print('Index %s does not exist' % index)