"""
.. module:: SearchIndex

SearchIndex
*************

:Description: SearchIndex

    Searches for a specific word in the field 'text' (--text)  or performs a query (--query) (LUCENE syntax,
    between single quotes) in the documents of an index (--index)
    

:Version: 

:Created on: 04/07/2018 

"""
from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

import argparse

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, required=True, help='Index to search')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='Lucene query')

    args = parser.parse_args()

    index = args.index
    if args.query:
        query = ' '.join(args.query)

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        q = Q('query_string',query=query)
        s = s.query(q)
        response = s[0:10].execute()

        for r in response:
            print('TITLE= %s URL=%s' % (r['title'], r['url']))
            print('DIRECTOR=%s' %  r['director'])
            print('DURATION=%s' %  r['duration'])
            print('MARK=%s' %  r['mark'])
            print('GENRE=%s' %  r['genre'])
            print('COUNTRY=%s' %  r['country'])
            print('YEAR=%s' %  r['year'])
            print('----------------------------------------')


        print ('%d Documents'% response.hits.total)
    except NotFoundError:
        print('Index %s does not exists' % index)

