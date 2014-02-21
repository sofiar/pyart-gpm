"""
pyart.io.radar
==============

A general central radial scanning (or dwelling) instrument class.

.. autosummary::
    :toctree: generated/

    Radar
    join_radar
    is_vpt
    to_vpt


"""
from __future__ import print_function

import copy
import sys

import numpy as np


class Radar:
    """
    A class for storing antenna coordinate radar data.

    The structure of the Radar class is based on the CF/Radial Data file
    format.  Global attributes and variables (section 4.1 and 4.3) are
    represented as a dictionary in the metadata attribute.  Other required and
    optional variables are represented as dictionaries in a attribute with the
    same name as the variable in the CF/Radial standard.  When a optional
    attribute not present the attribute has a value of None.  The data for a
    given variable is stored in the dictionary under the 'data' key.  Moment
    field data is stored as a dictionary of dictionaries in the fields
    attribute.  Sub-convention variables are stored as a dictionary of
    dictionaries under the meta_group attribute.

    Refer to the attribute section for information on the parameters.

    Attributes
    ----------
    time : dict
        Time at the center of each ray.
    range : dict
        Range to the center of each gate (bin).
    fields : dict of dicts
        Moment fields.
    metadata : dict
        Metadata describing the instrument and data.
    scan_type : str
        Type of scan, one of 'ppi', 'rhi', 'sector' or 'other'.  If the scan
        volume contains multiple sweep modes this should be 'other'.
    latitude : dict
        Latitude of the instrument.
    longitude : dict
        Longitude of the instrument.
    altitude : dict
        Altitude of the instrument, above sea level.
    altitude_agl : dict or None
        Altitude of the instrument above ground level.  If not provided this
        attribute is set to None, indicating this parameter not available.
    sweep_number : dict
        The number of the sweep in the volume scan, 0-based.
    sweep_mode : dict
        Sweep mode for each mode in the volume scan.
    fixed_angle : dict
        Target angle for thr sweep.  Azimuth angle in RHI modes, elevation
        angle in all other modes.
    sweep_start_ray_index : dict
        Index of the first ray in each sweep relative to the start of the
        volume, 0-based.
    sweep_end_ray_index : dict
        Index of the last ray in each sweep relative to the start of the
        volume, 0-based.
    target_scan_rate : dict or None
        Intended scan rate for each sweep.  If not provided this attribute is
        set to None, indicating this parameter is not available.
    azimuth : dict
        Azimuth of antenna, relative to true North.
    elevation : dict
        Elevation of antenna, relative to the horizontal plane.
    scan_rate : dict or None
        Actual antenna scan rate.  If not provided this attribute is set to
        None, indicating this parameter is not available.
    antenna_transition : dict or None
        Flag indicating if the antenna is in transition, 1 = tes, 0 = no.
        If not provided this attribute is set to None, indicating this
        parameter is not available.
    instruments_parameters : dict of dicts or None
        Instrument parameters, if not provided this attribute is set to None,
        indicating these parameters are not avaiable.  This dictionary also
        includes variables in the radar_parameters CF/Radial subconvention.
    radar_calibration : dict of dicts or None
        Instrument calibration parameters.  If not provided this attribute is
        set to None, indicating these parameters are not available
    ngates : int
        Number of gates (bins) in the volume.
    nrays : int
        Number of rays in the volume.
    nsweeps : int
        Number of sweep in the volume.

    """

    def __init__(self, time, _range, fields, metadata, scan_type,
                 latitude, longitude, altitude,

                 sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index,
                 sweep_end_ray_index,

                 azimuth, elevation,

                 altitude_agl=None,
                 target_scan_rate=None,

                 scan_rate=None, antenna_transition=None,

                 instrument_parameters=None,
                 radar_calibration=None,

                 ):

        if 'calendar' not in time:
            time['calendar'] = 'gregorian'
        self.time = time
        self.range = _range

        self.fields = fields
        self.metadata = metadata
        self.scan_type = scan_type

        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.altitude_agl = altitude_agl  # optional

        self.sweep_number = sweep_number
        self.sweep_mode = sweep_mode
        self.fixed_angle = fixed_angle
        self.sweep_start_ray_index = sweep_start_ray_index
        self.sweep_end_ray_index = sweep_end_ray_index
        self.target_scan_rate = target_scan_rate  # optional

        self.azimuth = azimuth
        self.elevation = elevation
        self.scan_rate = scan_rate  # optional
        self.antenna_transition = antenna_transition  # optional

        self.instrument_parameters = instrument_parameters  # optional
        self.radar_calibration = radar_calibration  # optional

        self.ngates = len(_range['data'])
        self.nrays = len(time['data'])
        self.nsweeps = len(sweep_number['data'])

    def info(self, level='standard', out=sys.stdout):
        """
        Print information on radar.

        Parameters
        ----------
        level : {'compact', 'standard', 'full', 'c', 's', 'f'}
            Level of information on radar object to print, compact is
            minimal information, standard more and full everything.
        out : file-like
            Stream to direct output to, default is to print information
            to standard out (the screen).

        """
        if level == 'c':
            level = 'compact'
        elif level == 's':
            level = 'standard'
        elif level == 'f':
            level = 'full'

        if level not in ['standard', 'compact', 'full']:
            raise ValueError('invalid level parameter')

        self._dic_info('altitude', level, out)
        self._dic_info('altitude_agl', level, out)
        self._dic_info('antenna_transition', level, out)
        self._dic_info('azimuth', level, out)
        self._dic_info('elevation', level, out)

        print('fields:', file=out)
        for field_name, field_dic in self.fields.iteritems():
            self._dic_info(field_name, level, out, field_dic, 1)

        self._dic_info('fixed_angle', level, out)

        if self.instrument_parameters is None:
            print('instrument_parameters: None', file=out)
        else:
            print('instrument_parameters:', file=out)
            for name, dic in self.instrument_parameters.iteritems():
                self._dic_info(name, level, out, dic, 1)

        self._dic_info('latitude', level, out)
        self._dic_info('longitude', level, out)

        print('nsweeps:', self.nsweeps, file=out)
        print('ngates:', self.ngates, file=out)
        print('nrays:', self.nrays, file=out)

        if self.radar_calibration is None:
            print('radar_calibration: None', file=out)
        else:
            print('radar_calibration:', file=out)
            for name, dic in self.radar_calibration.iteritems():
                self._dic_info(name, level, out, dic, 1)

        self._dic_info('range', level, out)
        self._dic_info('scan_rate', level, out)
        print('scan_type:', self.scan_type, file=out)
        self._dic_info('sweep_end_ray_index', level, out)
        self._dic_info('sweep_mode', level, out)
        self._dic_info('sweep_number', level, out)
        self._dic_info('sweep_start_ray_index', level, out)
        self._dic_info('target_scan_rate', level, out)
        self._dic_info('time', level, out)

        # always print out all metadata last
        self._dic_info('metadata', 'full', out)

    def _dic_info(self, attr, level, out, dic=None, ident_level=0):
        """ Print information on a dictionary attribute. """
        if dic is None:
            dic = getattr(self, attr)

        ilvl0 = '\t' * ident_level
        ilvl1 = '\t' * (ident_level + 1)

        if dic is None:
            print(attr + ': None', file=out)
            return

        # make a string summary of the data key if it exists.
        if 'data' not in dic:
            d_str = 'Missing'
        elif not isinstance(dic['data'], np.ndarray):
            d_str = '<not a ndarray>'
        else:
            data = dic['data']
            t = (data.dtype, data.shape)
            d_str = '<ndarray of type: %s and shape: %s>' % t

        # compact, only data summary
        if level == 'compact':
            print(ilvl0 + attr + ':', d_str, file=out)

        # standard, all keys, only summary for data
        elif level == 'standard':
            print(ilvl0 + attr + ':', file=out)
            print(ilvl1 + 'data:', d_str, file=out)
            for key, val in dic.iteritems():
                if key == 'data':
                    continue
                print(ilvl1 + key + ':', val, file=out)

        # full, all keys, full data
        elif level == 'full':
            print(attr + ':', file=out)
            if 'data' in dic:
                print(ilvl1 + 'data:', dic['data'], file=out)
            for key, val in dic.iteritems():
                if key == 'data':
                    continue
                print(ilvl1 + key + ':', val, file=out)

        return

    def add_field(self, field_name, dic):
        """
        Add a field to the object.

        Parameters
        ----------
        field_name : str
            Name of the field to add to the dictionary of fields.
        dic : dict
            Dictionary contain field data and metadata.

        """
        # check that the field dictionary to add is valid
        if field_name in self.fields:
            err = 'A field with name: %s already exists' % (field_name)
            raise ValueError(err)
        if 'data' not in dic:
            raise KeyError("dic must contain a 'data' key")
        if dic['data'].shape != (self.nrays, self.ngates):
            t = (self.nrays, self.ngates)
            err = "'data' has invalid shape, should be (%i, %i)" % t
            raise ValueError(err)
        # add the field
        self.fields[field_name] = dic
        return

    def add_field_like(self, existing_field_name, field_name, data):
        """
        Add a field to the object with metadata from a existing field.

        Parameters
        ----------
        existing_field_name : str
            Name of an existing field to take metadata from when adding
            the new field to the object.
        field_name : str
            Name of the field to add to the dictionary of fields.
        data : array
            Field data.

        """
        if existing_field_name not in self.fields:
            err = 'field %s does not exist in object' % (existing_field_name)
            raise ValueError(err)
        dic = self.fields[existing_field_name]
        dic['data'] = data
        return self.add_field(field_name, dic)

    def extract_sweeps(self, sweeps):
        """
        Create a new radar contains only the data from select sweeps.

        Parameters
        ----------
        sweeps : array_like
            Sweeps (0-based) to include in new Radar object.

        Returns
        -------
        radar : Radar
            Radar object which contains a copy of data from the selected
            sweeps.

        """

        # parse and verify parameters
        sweeps = np.array(sweeps, dtype='int32')
        if np.any(sweeps > (self.nsweeps - 1)):
            raise ValueError('invalid sweeps indices in sweeps parameter')
        if np.any(sweeps < 0):
            raise ValueError('only positive sweeps can be extracted')

        def mkdic(dic, select):
            """ Make a dictionary, selecting out select from data key """
            if dic is None:
                return None
            d = dic.copy()
            if 'data' in d and select is not None:
                d['data'] = d['data'][select].copy()
            return d

        # create array of rays which select the sweeps selected and
        # the number of rays per sweep.
        ray_count = (self.sweep_end_ray_index['data'] -
                     self.sweep_start_ray_index['data'] + 1)[sweeps]
        ssri = self.sweep_start_ray_index['data'][sweeps]
        rays = np.concatenate(
            [range(s, s+e) for s, e in zip(ssri, ray_count)]).astype('int32')

        # radar location attribute dictionary selector
        if len(self.altitude['data']) == 1:
            loc_select = None
        else:
            loc_select = sweeps

        # create new dictionaries
        time = mkdic(self.time, rays)
        _range = mkdic(self.range, None)

        fields = {}
        for field_name, dic in self.fields.iteritems():
            fields[field_name] = mkdic(dic, rays)
        metadata = mkdic(self.metadata, None)
        scan_type = str(self.scan_type)

        latitude = mkdic(self.latitude, loc_select)
        longitude = mkdic(self.longitude, loc_select)
        altitude = mkdic(self.altitude, loc_select)
        altitude_agl = mkdic(self.altitude_agl, loc_select)

        sweep_number = mkdic(self.sweep_number, sweeps)
        sweep_mode = mkdic(self.sweep_mode, sweeps)
        fixed_angle = mkdic(self.fixed_angle, sweeps)
        sweep_start_ray_index = mkdic(self.sweep_start_ray_index, None)
        sweep_start_ray_index['data'] = np.cumsum(np.append([0],
                                                  ray_count[:-1]))
        sweep_end_ray_index = mkdic(self.sweep_end_ray_index, None)
        sweep_end_ray_index['data'] = np.cumsum(ray_count) - 1
        target_scan_rate = mkdic(self.target_scan_rate, sweeps)

        azimuth = mkdic(self.azimuth, rays)
        elevation = mkdic(self.elevation, rays)
        scan_rate = mkdic(self.scan_rate, rays)
        antenna_transition = mkdic(self.antenna_transition, rays)

        # instrument_parameters
        # Filter the instrument_parameter dictionary based size of leading
        # dimension, this might not always be correct.
        if self.instrument_parameters is None:
            instrument_parameters = None
        else:
            instrument_parameters = {}
            for key, dic in self.instrument_parameters.iteritems():
                if dic['data'].ndim != 0:
                    dim0_size = dic['data'].shape[0]
                else:
                    dim0_size = -1
                if dim0_size == self.nsweeps:
                    fdic = mkdic(dic, sweeps)
                elif dim0_size == self.nrays:
                    fdic = mkdic(dic, rays)
                else:   # keep everything
                    fdic = mkdic(dic, None)
                instrument_parameters[key] = fdic

        # radar_calibration
        # copy all field in radar_calibration as is except for
        # r_calib_index which we filter based upon time.  This might
        # leave some indices in the "r_calib" dimension not referenced in
        # the r_calib_index array.
        if self.radar_calibration is None:
            radar_calibration = None
        else:
            radar_calibration = {}
            for key, dic in self.radar_calibration.iteritems():
                if key == 'r_calib_index':
                    radar_calibration[key] = mkdic(dic, rays)
                else:
                    radar_calibration[key] = mkdic(dic, None)

        return Radar(time, _range, fields, metadata, scan_type,
                     latitude, longitude, altitude,
                     sweep_number, sweep_mode, fixed_angle,
                     sweep_start_ray_index, sweep_end_ray_index,
                     azimuth, elevation,
                     altitude_agl=altitude_agl,
                     target_scan_rate=target_scan_rate,
                     scan_rate=scan_rate,
                     antenna_transition=antenna_transition,
                     instrument_parameters=instrument_parameters,
                     radar_calibration=radar_calibration)


def is_vpt(radar, offset=0.5):
    """
    Determine if a Radar appears to be a vertical pointing scan.

    This function only verifies that the object is a vertical pointing scan,
    use the :py:func:`to_vpt` function to convert the radar to a vpt scan
    if this function returns True.

    Parameters
    ----------
    radar : Radar
        Radar object to determine if
    offset : float
        Maximum offset of the elevation from 90 degrees to still consider
        to be vertically pointing.

    Returns
    -------
    flag : bool
        True if the radar appear to be verticle pointing, False if not.

    """
    # check that the elevation is within offset of 90 degrees.
    elev = radar.elevation['data']
    return np.all((elev < 90.0 + offset) & (elev > 90.0 - offset))


def to_vpt(radar, single_scan=True):
    """
    Convert an existing Radar object to represent a vertical pointing scan.

    This function does not verify that the Radar object contains a vertical
    pointing scan.  To perform such a check use :py:func:`is_vpt`.

    Parameters
    ----------
    radar : Radar
        Mislabeled vertical pointing scan Radar object to convert to be
        properly labeled.  This object is converted in place, no copy of
        the existing data is made.
    single_scan : bool, optional
        True to convert the volume to a single scan, any azimuth angle data
        is lost.  False will convert the scan to contain the same number of
        scans as rays, azimuth angles are retained.

    """
    if single_scan:
        nsweeps = 1
        radar.azimuth['data'][:] = 0.0
        seri = np.array([radar.nrays - 1], dtype='int32')
        radar.sweep_end_ray_index['data'] = seri
    else:
        nsweeps = radar.nrays
        # radar.azimuth not adjusted
        radar.sweep_end_ray_index['data'] = np.arange(nsweeps, dtype='int32')

    radar.scan_type = 'vpt'
    radar.nsweeps = nsweeps
    radar.target_scan_rate = None       # no scanning
    radar.elevation['data'][:] = 90.0

    radar.sweep_number['data'] = np.arange(nsweeps, dtype='int32')
    radar.sweep_mode['data'] = np.array(['vertical_pointing'] * nsweeps)
    radar.fixed_angle['data'] = np.ones(nsweeps, dtype='float32') * 90.0
    radar.sweep_start_ray_index['data'] = np.arange(nsweeps, dtype='int32')

    if radar.instrument_parameters is not None:
        for key in ['prt_mode', 'follow_mode', 'polarization_mode']:
            if key in radar.instrument_parameters:
                ip_dic = radar.instrument_parameters[key]
                ip_dic['data'] = np.array([ip_dic['data'][0]] * nsweeps)

    # Attributes that do not need any changes
    # radar.altitude
    # radar.altitude_agl
    # radar.latitude
    # radar.longitude

    # radar.range
    # radar.ngates
    # radar.nrays

    # radar.metadata
    # radar.radar_calibration

    # radar.time
    # radar.fields
    # radar.antenna_transition
    # radar.scan_rate
    return


def join_radar(radar1, radar2):

    #must have same gate spacing
    new_radar = copy.deepcopy(radar1)
    new_radar.azimuth['data'] = np.append(radar1.azimuth['data'],
                                          radar2.azimuth['data'])
    new_radar.elevation['data'] = np.append(radar1.elevation['data'],
                                            radar2.elevation['data'])

    if len(radar1.range['data']) >= len(radar2.range['data']):
        new_radar.range['data'] = radar1.range['data']
    else:
        new_radar.range['data'] = radar2.range['data']
    new_radar.time['data'] = np.append(radar1.time['data'],
                                       radar2.time['data'])

    for var in new_radar.fields.keys():
        sh1 = radar1.fields[var]['data'].shape
        sh2 = radar2.fields[var]['data'].shape
        print(sh1, sh2)
        new_field = np.ma.zeros([sh1[0] + sh2[0],
                                max([sh1[1], sh2[1]])]) - 9999.0
        new_field[0:sh1[0], 0:sh1[1]] = radar1.fields[var]['data']
        new_field[sh1[0]:, 0:sh2[1]] = radar2.fields[var]['data']
        new_radar.fields[var]['data'] = new_field

    # radar locations
    # TODO moving platforms
    lat1 = float(radar1.latitude['data'])
    lon1 = float(radar1.longitude['data'])
    alt1 = float(radar1.altitude['data'])
    lat2 = float(radar2.latitude['data'])
    lon2 = float(radar2.longitude['data'])
    alt2 = float(radar2.altitude['data'])

    if (lat1 != lat2) or (lon1 != lon2) or (alt1 != alt2):
        ones1 = np.ones(len(radar1.time['data']), dtype='float32')
        ones2 = np.ones(len(radar2.time['data']), dtype='float32')
        new_radar.latitude['data'] = np.append(ones1 * lat1, ones2 * lat2)
        new_radar.longitude['data'] = np.append(ones1 * lon1, ones2 * lon2)
        new_radar.latitude['data'] = np.append(ones1 * alt1, ones2 * alt2)
    else:
        new_radar.latitude = radar1.latitude['data']
        new_radar.longitude = radar1.latitude['data']
        new_radar.altitude = radar1.altitude['data']
    return new_radar
