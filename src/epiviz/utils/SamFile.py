'''
Created on Nov 6, 2013

@author: florin
'''

import re

from pandas import DataFrame
from pandas import concat

from epiviz.utils.IntervalTree import Interval
from epiviz.utils.IntervalTree import IntervalTree


SEGMENT_UNMAPPED = 4

class SamFile(object):
    '''
    Contains the base functionality for sam file processing and a static method called parse(filename),
    that constructs a SamFile instance, given a system file path.
    '''
    def __init__(self, header, alignments):
        '''
        Constructor
        '''
        self._header = header
        self._alignments = alignments
        self._alignment_forest = {}
        self._alns_by_ref = {}

        # Partition alignments by reference
        for aln in alignments:
            if aln.is_unmapped():
                continue
            if aln.reference() not in self._alns_by_ref:
                self._alns_by_ref[aln.reference()] = []
            self._alns_by_ref[aln.reference()].append(aln)

        for ref, alns in self._alns_by_ref.iteritems():
            self._alignment_forest[ref] = IntervalTree(alns)

    def coverage(self, reference, start, length):
        '''
        Gets all alignments corresponding to the given region in the genome
        :param reference:
        :param start:
        :param length:
        '''
        return self._alignment_forest[reference].search(start, start + length - 1)

    def base_pair_coverage(self, reference, start, length):
        '''
        Returns a list of base-pair, coverage tuples. It is assumed that the same coverage
        applies to all following base-pairs until the next entry
        :param reference:
        :param start:
        :param length:
        '''
        alns = self.coverage(reference, start, length)

        if len(alns) == 0:
            # return [(start, 0)]
            return DataFrame({'start': [], 'end': [], 'value': []})

        return SamFile._compute_base_pair_coverage(alns)

    def whole_genome_coverage_by_ref(self):
        '''
        Returns a map of references as keys and an array of tuples of base-pair, coverage
        '''
        result = {}

        for ref, alns in self._alns_by_ref.iteritems():
            result[ref] = SamFile._compute_base_pair_coverage(alns)

        return result

    def whole_genome_coverage(self):
        '''
        Returns a map of references as keys and an array of tuples of base-pair, coverage
        '''
        pieces = []

        for _, alns in self._alns_by_ref.iteritems():
            pieces.append(SamFile._compute_base_pair_coverage(alns))

        return concat(pieces, ignore_index=True)


    def alignments(self):
        return self._alignments

    @staticmethod
    def _compute_base_pair_coverage(alignments):
        if len(alignments) == 0:
            return []

        # First we make a list of all starts and ends, keeping track, for each of the alignment they came from
        points = []
        for i in range(len(alignments)):
            points.append((alignments[i].pos(), i, alignments[i].reference()))
            points.append((alignments[i].pos() + alignments[i].length(), i, alignments[i].reference()))

        # Second, we sort the list by these points
        points = sorted(points, key=lambda point: point[0])

        # Finally, we compute coverage
        coverage = {'seqName': [], 'start': [], 'end': [], 'coverage': []}
        open_alns = {}

        overlaps = 0
        last = points[0][0]

        for i in range(0, len(points)):
            if points[i][0] != last:
                # coverage.append((last, overlaps))
                coverage['start'].append(last)
                coverage['end'].append(points[i][0])
                coverage['coverage'].append(overlaps)
                coverage['seqName'].append(points[i][2])

            if points[i][1] in open_alns:
                overlaps -= 1
                del open_alns[points[i][1]]
            else:
                overlaps += 1
                open_alns[points[i][1]] = True

            last = points[i][0]

        return DataFrame(coverage)

    @staticmethod
    def read(filename):
        '''
        :param filename:
        '''
        try:
            header = []
            alignments = []
            with open(filename) as f:
                for line in f:
                    if line.startswith('@'):
                        # header line
                        header.append(HeaderEntry.parse(line))
                        continue

                    alignments.append(Alignment.parse(line))

            return SamFile(header, alignments)

        except EnvironmentError as err:
            print "Unable to open file: {}".format(err)

class HeaderEntry(object):
    '''
    Contains information from the header. Right now, the class has just one field called _text,
    containing one line of header information. This class was created for potential future use,
    in case we care about the headers in the sam file.
    '''
    def __init__(self, text):
        '''
        '''
        self._text = text

    def __str__(self):
        '''
        Returns a string representation of the header line
        '''
        return self._text

    @staticmethod
    def parse(text):
        '''
        Parses the given line of text and returns an instance of HeaderEntry
        if successful, or throws an exception otherwise.
        :param text:
        '''
        return HeaderEntry(text)

class Alignment(Interval):
    '''
    Handles parsing of individual entries in the sam file, with the main columns defined in the
    sam file format
    '''
    def __init__(self, text, qname, flag, rname, pos, mapq, cigar, rnext, pnext, tlen, seq, qual):
        '''
        :test_param text: The original string from which this alignment comes from
        :test_param qname:
        :test_param flag:
        :test_param rname:
        :test_param pos:
        :test_param mapq:
        :test_param cigar:
        :test_param rnext:
        :test_param pnext:
        :test_param tlen:
        :test_param seq:
        :test_param qual:
        '''

        self._text = text
        self._qname = qname
        self._flag = flag
        self._rname = rname
        self._pos = pos
        self._mapq = mapq
        self._cigar = cigar
        self._rnext = rnext
        self._pnext = pnext
        self._tlen = tlen
        self._seq = seq
        self._qual = qual

        self._alignment_length = -1
        self._calc_length()

        super(Alignment, self).__init__(self._pos if not self.is_unmapped() else None, self._pos + self._alignment_length - 1 if not self.is_unmapped() else None)

    def __str__(self):
        return self._text

    @staticmethod
    def parse(text):
        '''
        Parses the given line of text and returns an instance of Alignment
        if successful, or throws an exception otherwise.
        '''
        tokens = text.split('\t')
        flag = int(tokens[1])
        return Alignment(
            text,
            tokens[0],  # qname
            flag,
            tokens[2],  # rname
            int(tokens[3]) if not flag & SEGMENT_UNMAPPED else None,  # pos
            int(tokens[4]),  # mapq
            tokens[5],  # cigar
            tokens[6],  # rnext
            int(tokens[7]),  # pnext
            int(tokens[8]),  # tlen
            tokens[9],  # seq
            tokens[10])  # qual

    def qname(self):
        return self._qname

    def flag(self):
        return self._flag

    def is_unmapped(self):
        return self._flag & SEGMENT_UNMAPPED

    def reference(self):
        '''
        Gets the id of the reference sequence
        '''
        return self._rname

    def pos(self):
        '''
        Gets the start position of the alignment in the reference sequence
        '''
        return self._pos

    def cigar(self):
        return self._cigar

    def seq(self):
        return self._seq

    def length(self):
        return self._alignment_length

    def _calc_length(self):
        '''
        Computes the exact overlap calc_length between the read and the reference
        '''
        if self._alignment_length >= 0:
            return self._alignment_length

        if self._flag & SEGMENT_UNMAPPED:
            self._alignment_length = 0
            return self._alignment_length

        # Count number of insertions and deletions in the CIGAR string
        # to find out how big the actual alignment is
        length = len(self._seq)

        # First, split string into operators
        op_groups = filter(None, re.split('([0-9]+[MIDNHP=X])', self._cigar))

        # For each group of operations of the same type, decrease computed calc_length
        # if operator is D(elete) and increase calc_length if it's I(nsert)
        for group in op_groups:
            couple = filter(None, re.split('([0-9]+|[MIDNHP=X])', group))
            # print couple
            (count, op) = couple
            if op == 'D':
                length += int(count)
            elif op == 'I':
                length -= int(count)

        self._alignment_length = length
        return self._alignment_length
