'''
Interval Tree implementation in Python
Copyright (C) 2010  Tyler Kahn

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

class IntervalTree(object):
    def __init__(self, intervals):
        self._top_node = self.divide_intervals(intervals)

    def divide_intervals(self, intervals):

        if not intervals:
            return None

        x_center = self.center(intervals)

        s_center = []
        s_left = []
        s_right = []

        for k in intervals:
            if k.end() < x_center:
                s_left.append(k)
            elif k.start() > x_center:
                s_right.append(k)
            else:
                s_center.append(k)

        return Node(x_center, s_center, self.divide_intervals(s_left), self.divide_intervals(s_right))


    def center(self, intervals):
        fs = sort_by_start(intervals)
        calc_length = len(fs)

        return fs[int(calc_length / 2)].start()

    def search(self, start, end=None):
        if end:
            result = []
            for j in xrange(start, end + 1):
                for k in self.search(j):
                    result.append(k)
                result = list(set(result))
            return sort_by_start(result)
        else:
            return self._search(self._top_node, start, [])

    def _search(self, node, point, result):
        for k in node.s_center:
            if k.start() <= point <= k.end():
                result.append(k)
        if point < node.x_center and node.left_node:
            for k in self._search(node.left_node, point, []):
                result.append(k)
        if point > node.x_center and node.right_node:
            for k in self._search(node.right_node, point, []):
                result.append(k)

        return list(set(result))

class Interval(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

    def start(self):
        return self._start
    def end(self):
        return self._end

class Node(object):
    def __init__(self, x_center, s_center, left_node, right_node):
        self.x_center = x_center
        self.s_center = sort_by_start(s_center)
        self.left_node = left_node
        self.right_node = right_node

def sort_by_start(intervals):
    return sorted(intervals, key=lambda x: x.start())

