'''
Created on Mar 13, 2014

@author: florin
'''
from epiviz.events.Event import Event
from epiviz.exceptions.EpiVizException import EpiVizException


class DataStore(object):
    '''

    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._data_added = Event()
        self._data_removed = Event()

        self._store = {}  # A map with keys datasource_id, and values {data, datasource_group, measurements, min, max}

        self._measurements = {
            'id': [],
            'name': [],
            'type': [],
            'datasourceId': [],
            'datasourceGroup': [],
            'defaultChartType': [],
            'annotation': [],
            'minValue': [],
            'maxValue': [],
            'metadata': []}

        self._seq_infos = {}

    def on_data_added(self):
        return self._data_added

    def on_data_removed(self):
        return self._data_removed

    def add_data(self, data, datasource_id, datasource_group, measurements, names, min_vals, max_vals, metadata):
        '''
        :param data: DataFrame
        :param datasource_id: the name of the datasource
        :param datasource_group: identifies multiple data sources with the same start, end and index
        :param measurements: a list of columns in the data frame that will be treated as measurements
        :param names: a list of human readable names for the measurements
        :param minVals: a list of min values for the given list of columns
        :param maxVals: a list of max values for the given list of columns
        :param metadata: a list of columns in the data frame that contain metadata about the rows
        '''

        if datasource_id in self._store:
            raise EpiVizException('datasource_id %s already in data store' % datasource_id)

        data_tuple = {
           'data': data,
           'datasource_id': datasource_id,
           'datasource_group': datasource_group,
           'measurements': measurements,
           'names': names,
           'minVals': min_vals,
           'maxVals': max_vals,
           'metadata': metadata
        }

        self._store[datasource_id] = data_tuple

        if measurements:
            for i in range(len(measurements)):
                self._measurements['id'].append(measurements[i])
                self._measurements['name'].append(names[i])
                self._measurements['type'].append('feature')
                self._measurements['datasourceId'].append(datasource_id)
                self._measurements['datasourceGroup'].append(datasource_group)
                self._measurements['defaultChartType'].append('any')
                self._measurements['annotation'].append(None)
                self._measurements['minValue'].append(min_vals[i])
                self._measurements['maxValue'].append(max_vals[i])
                self._measurements['metadata'].append(metadata)
        else:
            self._measurements['id'].append(datasource_id)
            self._measurements['name'].append(datasource_id)
            self._measurements['type'].append('range')
            self._measurements['datasourceId'].append(datasource_id)
            self._measurements['datasourceGroup'].append(datasource_group)
            self._measurements['defaultChartType'].append(None)
            self._measurements['annotation'].append(None)
            self._measurements['minValue'].append(None)
            self._measurements['maxValue'].append(None)
            self._measurements['metadata'].append(metadata)

        seq_names = set(data['seqName'])
        seq_infos = []
        for seq_name in seq_names:
            seq_info = self._seq_infos[seq_name] if seq_name in self._seq_infos else None
            changed = False
            if seq_info is None:
                seq_info = [seq_name, None, None]
                self._seq_infos[seq_name] = seq_info
                changed = True
            mn = data[data['seqName'] == seq_name]['start'].min().astype(int)
            mx = data[data['seqName'] == seq_name]['end'].max().astype(int)

            if seq_info[1] is None or mn < seq_info[1]:
                seq_info[1] = mn
                changed = True
            if seq_info[2] is None or mx > seq_info[2]:
                seq_info[2] = mx
                changed = True

            if changed:
                seq_infos.append(seq_info)

        data_tuple['seqInfos'] = seq_infos
        self._data_added.notify(data_tuple)  # Fire event


    def remove_data(self, datasource_id, measurements=None):
        '''
        :param datasource_id:
        :param measurements: the columns in the data source to remove; if this parameter is ignored, all measurements in the data source will be removed
        '''

        if not datasource_id in self._store:
            print 'datasource_id %s not in data store' % datasource_id
            return

        if not measurements:
            del self._store[datasource_id]
        elif self._store[datasource_id]['measurements']:
            new_ms = [m for m in self._store[datasource_id]['measurements'] if m not in set(measurements)]
            self._store[datasource_id]['measurements'] = new_ms

        self._data_removed.notify(datasource_id, measurements)

    def measurements(self):
        return self._measurements

    def rows(self, datasource_id, seq_name, start, end, metadata):
        '''
        :param datasource: string
        :param seq_name: string
        :param start: number
        :param end: number
        :param metadata: string[] A list of column names for which to retrieve the values
        Returns {globalStartIndex: number, values: {id: number[], start: number[], end: number[], strand: string|string[], metadata: map<string, string[]>}}
        '''

        # TODO: This is not optimized! Rewrite it so that it is!

        metadata_values = None
        if metadata:
            metadata_values = {}
            for col in metadata:
                metadata_values[col] = []
        empty = {
          'globalStartIndex': None,
          'values': {
            'id': [],
            'start': [],
            'end': [],
            'strand': '*',
            'metadata': metadata_values}}

        if not (datasource_id in self._store):
            return empty

        data = self._store[datasource_id]['data']
        selection = data[(data['seqName'] == seq_name) & (data['end'] > start) & (data['start'] < end)]

        if len(selection) == 0:
            return empty

        min_index = min(selection.index).astype(int)
        max_index = max(selection.index).astype(int)

        rows = data[min_index:(max_index + 1)]

        metadata_values = None
        if metadata:
            metadata_values = {}
            for col in metadata:
                metadata_values[col] = rows[col].values.tolist()

        return {
            'globalStartIndex': min_index,
            'values': {
                'id': rows.index.values.tolist(),
                'start': rows['start'].values.tolist(),
                'end': rows['end'].values.tolist(),
                'strand': '*' if not 'strand' in data else rows['strand'].values.tolist(),
                'metadata': metadata_values}}

    def values(self, measurement, datasource_id, seq_name, start, end):
        '''
        :param measurement:
        :param datasource_id:
        :param seq_name:
        :param start:
        :param end:
        Returns {globalStartIndex: number, values: number[]}
        '''

        if not (datasource_id in self._store):
            return {'globalStartIndex': None, 'values': []}

        data = self._store[datasource_id]['data']

        if not (measurement in data):
            return {'globalStartIndex': None, 'values': []}

        selection = data[(data['seqName'] == seq_name) & (data['end'] > start) & (data['start'] < end)]

        if len(selection) == 0:
            return {'globalStartIndex': None, 'values': []}

        min_index = min(selection.index).astype(int)
        max_index = max(selection.index).astype(int)

        rows = data[min_index:(max_index + 1)]

        return {'globalStartIndex': min_index, 'values': rows[measurement].values.tolist()}

    def seq_infos(self):
        return self._seq_infos.values()

