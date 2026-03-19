/repo/src/awkward/operations/structure.py:def packed(array, highlevel=True, behavior=None):
2336:def packed(array, highlevel=True, behavior=None):
2050:            layout = _pack_layout(layout)
2157:def _pack_layout(layout):
2392:            transform, _pack_layout(layout), depth, user
Here's the content of /repo/src/awkward/operations/structure.py with line numbers (which has a total of 4643 lines) with view_range=[2157, 2340]:
  2157	def _pack_layout(layout):
  2158	    nplike = ak.nplike.of(layout)
  2159	
  2160	    if isinstance(layout, ak.layout.NumpyArray):
  2161	        return layout.contiguous()
  2162	
  2163	    # EmptyArray is a no-op
  2164	    elif isinstance(layout, ak.layout.EmptyArray):
  2165	        return layout
  2166	
  2167	    # Project indexed arrays
  2168	    elif isinstance(layout, ak._util.indexedoptiontypes):
  2169	        if isinstance(layout.content, ak._util.optiontypes):
  2170	            return layout.simplify()
  2171	
  2172	        index = nplike.asarray(layout.index)
  2173	        new_index = nplike.zeros_like(index)
  2174	
  2175	        is_none = index < 0
  2176	        new_index[is_none] = -1
  2177	        new_index[~is_none] = nplike.arange(len(new_index) - nplike.sum(is_none))
  2178	
  2179	        return ak.layout.IndexedOptionArray64(
  2180	            ak.layout.Index64(new_index),
  2181	            layout.project(),
  2182	            layout.identities,
  2183	            layout.parameters,
  2184	        )
  2185	
  2186	    # Project indexed arrays
  2187	    elif isinstance(layout, ak._util.indexedtypes):
  2188	        return layout.project()
  2189	
  2190	    # ListArray performs both ordering and resizing
  2191	    elif isinstance(
  2192	        layout,
  2193	        (
  2194	            ak.layout.ListArray32,
  2195	            ak.layout.ListArrayU32,
  2196	            ak.layout.ListArray64,
  2197	        ),
  2198	    ):
  2199	        return layout.toListOffsetArray64(True)
  2200	
  2201	    # ListOffsetArray performs resizing
  2202	    elif isinstance(
  2203	        layout,
  2204	        (
  2205	            ak.layout.ListOffsetArray32,
  2206	            ak.layout.ListOffsetArray64,
  2207	            ak.layout.ListOffsetArrayU32,
  2208	        ),
  2209	    ):
  2210	        new_layout = layout.toListOffsetArray64(True)
  2211	        new_length = new_layout.offsets[-1]
  2212	        return ak.layout.ListOffsetArray64(
  2213	            new_layout.offsets,
  2214	            new_layout.content[:new_length],
  2215	            new_layout.identities,
  2216	            new_layout.parameters,
  2217	        )
  2218	
  2219	    # UnmaskedArray just wraps another array
  2220	    elif isinstance(layout, ak.layout.UnmaskedArray):
  2221	        return ak.layout.UnmaskedArray(
  2222	            layout.content, layout.identities, layout.parameters
  2223	        )
  2224	
  2225	    # UnionArrays can be simplified
  2226	    # and their contents too
  2227	    elif isinstance(layout, ak._util.uniontypes):
  2228	        layout = layout.simplify()
  2229	
  2230	        # If we managed to lose the drop type entirely
  2231	        if not isinstance(layout, ak._util.uniontypes):
  2232	            return layout
  2233	
  2234	        # Pack simplified layout
  2235	        tags = nplike.asarray(layout.tags)
  2236	        index = nplike.asarray(layout.index)
  2237	
  2238	        new_contents = [None] * len(layout.contents)
  2239	        new_index = nplike.zeros_like(index)
  2240	
  2241	        # Compact indices
  2242	        for i in range(len(layout.contents)):
  2243	            is_i = tags == i
  2244	
  2245	            new_contents[i] = layout.project(i)
  2246	            new_index[is_i] = nplike.arange(nplike.sum(is_i))
  2247	
  2248	        return ak.layout.UnionArray8_64(
  2249	            ak.layout.Index8(tags),
  2250	            ak.layout.Index64(new_index),
  2251	            new_contents,
  2252	            layout.identities,
  2253	            layout.parameters,
  2254	        )
  2255	
  2256	    # RecordArray contents can be truncated
  2257	    elif isinstance(layout, ak.layout.RecordArray):
  2258	        return ak.layout.RecordArray(
  2259	            [c[: len(layout)] for c in layout.contents],
  2260	            layout.recordlookup,
  2261	            len(layout),
  2262	            layout.identities,
  2263	            layout.parameters,
  2264	        )
  2265	
  2266	    # RegularArrays can change length
  2267	    elif isinstance(layout, ak.layout.RegularArray):
  2268	        if not len(layout):
  2269	            return layout
  2270	
  2271	        content = layout.content
  2272	
  2273	        # Truncate content to perfect multiple of the RegularArray size
  2274	        if layout.size > 0:
  2275	            r = len(content) % layout.size
  2276	            content = content[: len(content) - r]
  2277	        else:
  2278	            content = content[:0]
  2279	
  2280	        return ak.layout.RegularArray(
  2281	            content,
  2282	            layout.size,
  2283	            len(layout),
  2284	            layout.identities,
  2285	            layout.parameters,
  2286	        )
  2287	
  2288	    # BitMaskedArrays can change length
  2289	    elif isinstance(layout, ak.layout.BitMaskedArray):
  2290	        layout = layout.simplify()
  2291	
  2292	        if not isinstance(ak.type(layout.content), ak.types.PrimitiveType):
  2293	            return layout.toIndexedOptionArray64()
  2294	
  2295	        return ak.layout.BitMaskedArray(
  2296	            layout.mask,
  2297	            layout.content[: len(layout)],
  2298	            layout.valid_when,
  2299	            len(layout),
  2300	            layout.lsb_order,
  2301	            layout.identities,
  2302	            layout.parameters,
  2303	        )
  2304	
  2305	    # ByteMaskedArrays can change length
  2306	    elif isinstance(layout, ak.layout.ByteMaskedArray):
  2307	        layout = layout.simplify()
  2308	
  2309	        if not isinstance(ak.type(layout.content), ak.types.PrimitiveType):
  2310	            return layout.toIndexedOptionArray64()
  2311	
  2312	        return ak.layout.ByteMaskedArray(
  2313	            layout.mask,
  2314	            layout.content[: len(layout)],
  2315	            layout.valid_when,
  2316	            layout.identities,
  2317	            layout.parameters,
  2318	        )
  2319	
  2320	    elif isinstance(layout, ak.layout.VirtualArray):
  2321	        return layout.array
  2322	
  2323	    elif isinstance(layout, ak.partition.PartitionedArray):
  2324	        return layout
  2325	
  2326	    elif isinstance(layout, ak.layout.Record):
  2327	        return layout
  2328	
  2329	    # Finally, fall through to failure
  2330	    else:
  2331	        raise AssertionError(
  2332	            "unrecognized layout: " + repr(layout) + ak._util.exception_suffix(__file__)
  2333	        )
  2334	
  2335	
  2336	def packed(array, highlevel=True, behavior=None):
  2337	    """
  2338	    Args:
  2339	        array: Array whose internal structure will be packed.
  2340	        highlevel (bool): If True, return an #ak.Array; otherwise, return
1216:            return transform_child_layouts(
1291:def transform_child_layouts(transform, layout, depth, user=None, keep_parameters=True):
Here's the content of /repo/src/awkward/_util.py with line numbers (which has a total of 1894 lines) with view_range=[1291, 1380]:
  1291	def transform_child_layouts(transform, layout, depth, user=None, keep_parameters=True):
  1292	    # the rest of this is one switch statement
  1293	    if isinstance(layout, ak.partition.PartitionedArray):
  1294	        return ak.partition.IrregularlyPartitionedArray(
  1295	            [transform(x, depth, user) for x in layout.partitions]
  1296	        )
  1297	
  1298	    elif isinstance(layout, ak.layout.NumpyArray):
  1299	        if keep_parameters:
  1300	            return layout
  1301	        else:
  1302	            return ak.layout.NumpyArray(
  1303	                ak.nplike.of(layout).asarray(layout), layout.identities, None
  1304	            )
  1305	
  1306	    elif isinstance(layout, ak.layout.EmptyArray):
  1307	        if keep_parameters:
  1308	            return layout
  1309	        else:
  1310	            return ak.layout.EmptyArray(layout.identities, None)
  1311	
  1312	    elif isinstance(layout, ak.layout.RegularArray):
  1313	        return ak.layout.RegularArray(
  1314	            transform(layout.content, depth + 1, user),
  1315	            layout.size,
  1316	            len(layout),
  1317	            layout.identities,
  1318	            layout.parameters if keep_parameters else None,
  1319	        )
  1320	
  1321	    elif isinstance(layout, ak.layout.ListArray32):
  1322	        return ak.layout.ListArray32(
  1323	            layout.starts,
  1324	            layout.stops,
  1325	            transform(layout.content, depth + 1, user),
  1326	            layout.identities,
  1327	            layout.parameters if keep_parameters else None,
  1328	        )
  1329	
  1330	    elif isinstance(layout, ak.layout.ListArrayU32):
  1331	        return ak.layout.ListArrayU32(
  1332	            layout.starts,
  1333	            layout.stops,
  1334	            transform(layout.content, depth + 1, user),
  1335	            layout.identities,
  1336	            layout.parameters if keep_parameters else None,
  1337	        )
  1338	
  1339	    elif isinstance(layout, ak.layout.ListArray64):
  1340	        return ak.layout.ListArray64(
  1341	            layout.starts,
  1342	            layout.stops,
  1343	            transform(layout.content, depth + 1, user),
  1344	            layout.identities,
  1345	            layout.parameters if keep_parameters else None,
  1346	        )
  1347	
  1348	    elif isinstance(layout, ak.layout.ListOffsetArray32):
  1349	        return ak.layout.ListOffsetArray32(
  1350	            layout.offsets,
  1351	            transform(layout.content, depth + 1, user),
  1352	            layout.identities,
  1353	            layout.parameters if keep_parameters else None,
  1354	        )
  1355	
  1356	    elif isinstance(layout, ak.layout.ListOffsetArrayU32):
  1357	        return ak.layout.ListOffsetArrayU32(
  1358	            layout.offsets,
  1359	            transform(layout.content, depth + 1, user),
  1360	            layout.identities,
  1361	            layout.parameters if keep_parameters else None,
  1362	        )
  1363	
  1364	    elif isinstance(layout, ak.layout.ListOffsetArray64):
  1365	        return ak.layout.ListOffsetArray64(
  1366	            layout.offsets,
  1367	            transform(layout.content, depth + 1, user),
  1368	            layout.identities,
  1369	            layout.parameters if keep_parameters else None,
  1370	        )
  1371	
  1372	    elif isinstance(layout, ak.layout.IndexedArray32):
  1373	        return ak.layout.IndexedArray32(
  1374	            layout.index,
  1375	            transform(layout.content, depth, user),
  1376	            layout.identities,
  1377	            layout.parameters if keep_parameters else None,
  1378	        )
  1379	
  1380	    elif isinstance(layout, ak.layout.IndexedArrayU32):
Here's the content of /repo/src/awkward/_util.py with line numbers (which has a total of 1894 lines) with view_range=[1380, 1530]:
  1380	    elif isinstance(layout, ak.layout.IndexedArrayU32):
  1381	        return ak.layout.IndexedArrayU32(
  1382	            layout.index,
  1383	            transform(layout.content, depth, user),
  1384	            layout.identities,
  1385	            layout.parameters if keep_parameters else None,
  1386	        )
  1387	
  1388	    elif isinstance(layout, ak.layout.IndexedArray64):
  1389	        return ak.layout.IndexedArray64(
  1390	            layout.index,
  1391	            transform(layout.content, depth, user),
  1392	            layout.identities,
  1393	            layout.parameters if keep_parameters else None,
  1394	        )
  1395	
  1396	    elif isinstance(layout, ak.layout.IndexedOptionArray32):
  1397	        return ak.layout.IndexedOptionArray32(
  1398	            layout.index,
  1399	            transform(layout.content, depth, user),
  1400	            layout.identities,
  1401	            layout.parameters if keep_parameters else None,
  1402	        )
  1403	
  1404	    elif isinstance(layout, ak.layout.IndexedOptionArray64):
  1405	        return ak.layout.IndexedOptionArray64(
  1406	            layout.index,
  1407	            transform(layout.content, depth, user),
  1408	            layout.identities,
  1409	            layout.parameters if keep_parameters else None,
  1410	        )
  1411	
  1412	    elif isinstance(layout, ak.layout.ByteMaskedArray):
  1413	        return ak.layout.ByteMaskedArray(
  1414	            layout.mask,
  1415	            transform(layout.content, depth, user),
  1416	            layout.valid_when,
  1417	            layout.identities,
  1418	            layout.parameters if keep_parameters else None,
  1419	        )
  1420	
  1421	    elif isinstance(layout, ak.layout.BitMaskedArray):
  1422	        return ak.layout.BitMaskedArray(
  1423	            layout.mask,
  1424	            transform(layout.content, depth, user),
  1425	            layout.valid_when,
  1426	            len(layout),
  1427	            layout.lsb_order,
  1428	            layout.identities,
  1429	            layout.parameters if keep_parameters else None,
  1430	        )
  1431	
  1432	    elif isinstance(layout, ak.layout.UnmaskedArray):
  1433	        return ak.layout.UnmaskedArray(
  1434	            transform(layout.content, depth, user),
  1435	            layout.identities,
  1436	            layout.parameters if keep_parameters else None,
  1437	        )
  1438	
  1439	    elif isinstance(layout, ak.layout.RecordArray):
  1440	        return ak.layout.RecordArray(
  1441	            [transform(x, depth, user) for x in layout.contents],
  1442	            layout.recordlookup,
  1443	            len(layout),
  1444	            layout.identities,
  1445	            layout.parameters if keep_parameters else None,
  1446	        )
  1447	
  1448	    elif isinstance(layout, ak.layout.Record):
  1449	        return ak.layout.Record(
  1450	            transform(layout.array, depth, user),
  1451	            layout.at,
  1452	        )
  1453	
  1454	    elif isinstance(layout, ak.layout.UnionArray8_32):
  1455	        return ak.layout.UnionArray8_32(
  1456	            layout.tags,
  1457	            layout.index,
  1458	            [transform(x, depth, user) for x in layout.contents],
  1459	            layout.identities,
  1460	            layout.parameters if keep_parameters else None,
  1461	        )
  1462	
  1463	    elif isinstance(layout, ak.layout.UnionArray8_U32):
  1464	        return ak.layout.UnionArray8_U32(
  1465	            layout.tags,
  1466	            layout.index,
  1467	            [transform(x, depth, user) for x in layout.contents],
  1468	            layout.identities,
  1469	            layout.parameters if keep_parameters else None,
  1470	        )
  1471	
  1472	    elif isinstance(layout, ak.layout.UnionArray8_64):
  1473	        return ak.layout.UnionArray8_64(
  1474	            layout.tags,
  1475	            layout.index,
  1476	            [transform(x, depth, user) for x in layout.contents],
  1477	            layout.identities,
  1478	            layout.parameters if keep_parameters else None,
  1479	        )
  1480	
  1481	    elif isinstance(layout, ak.layout.VirtualArray):
  1482	        return transform(layout.array, depth, user)
  1483	
  1484	    else:
  1485	        raise AssertionError(
  1486	            "unrecognized Content type: {0}".format(type(layout))
  1487	            + exception_suffix(__file__)
  1488	        )
  1489	
  1490	
  1491	def find_caches(layout):
  1492	    # Both of the implementations below find referentially unique mutablemappings,
  1493	    # but the PartitionedArray case is optimized for many unique values (with a set)
  1494	    # and the non-partitioned case is optimized for few (O(n^2) algo, but no hashmap).
  1495	    if isinstance(layout, ak.partition.PartitionedArray):
  1496	        seen = set()
  1497	        mutablemappings = []
  1498	        for partition in layout.partitions:
  1499	            for cache in partition.caches:
  1500	                x = cache.mutablemapping
  1501	                if id(x) not in seen:
  1502	                    seen.add(id(x))
  1503	                    mutablemappings.append(x)
  1504	    else:
  1505	        mutablemappings = []
  1506	        for cache in layout.caches:
  1507	            x = cache.mutablemapping
  1508	            for y in mutablemappings:
  1509	                if x is y:
  1510	                    break
  1511	            else:
  1512	                mutablemappings.append(x)
  1513	
  1514	    return tuple(mutablemappings)
  1515	
  1516	
  1517	def highlevel_type(layout, behavior, isarray):
  1518	    if isarray:
  1519	        return ak.types.ArrayType(layout.type(typestrs(behavior)), len(layout))
  1520	    else:
  1521	        return layout.type(typestrs(behavior))
  1522	
  1523	
  1524	_is_identifier = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*$")
  1525	
  1526	
  1527	def minimally_touching_string(limit_length, layout, behavior):
  1528	    if isinstance(layout, ak.layout.Record):
  1529	        layout = layout.array[layout.at : layout.at + 1]
  1530
17:class Record(object):
Here's the content of /repo/src/awkward/_v2/record.py with line numbers (which has a total of 101 lines) with view_range=[17, 80]:
    17	class Record(object):
    18	    def __init__(self, array, at):
    19	        if not isinstance(array, ak._v2.contents.recordarray.RecordArray):
    20	            raise TypeError(
    21	                "Record 'array' must be a RecordArray, not {0}".format(repr(array))
    22	            )
    23	        if not ak._util.isint(at):
    24	            raise TypeError(
    25	                "Record 'at' must be an integer, not {0}".format(repr(array))
    26	            )
    27	        if 0 <= at < len(array):
    28	            self._array = array
    29	            self._at = at
    30	        else:
    31	            raise ValueError(
    32	                "Record 'at' must be >= 0 and < len(array) == {0}, not {1}".format(
    33	                    len(array), at
    34	                )
    35	            )
    36	
    37	    @property
    38	    def array(self):
    39	        return self._array
    40	
    41	    @property
    42	    def at(self):
    43	        return self._at
    44	
    45	    def __repr__(self):
    46	        return self._repr("", "", "")
    47	
    48	    def _repr(self, indent, pre, post):
    49	        out = [indent, pre, "\n")
    52	        out.append(self._array._repr(indent + "    ", "", "\n"))
    53	        out.append(indent)
    54	        out.append("")
    55	        out.append(post)
    56	        return "".join(out)
    57	
    58	    def __getitem__(self, where):
    59	        if ak._util.isint(where):
    60	            raise IndexError("scalar Record cannot be sliced by an integer")
    61	
    62	        elif isinstance(where, slice):
    63	            raise IndexError("scalar Record cannot be sliced by a range slice (`:`)")
    64	
    65	        elif ak._util.isstr(where):
    66	            return self._getitem_field(where)
    67	
    68	        elif where is np.newaxis:
    69	            raise IndexError("scalar Record cannot be sliced by np.newaxis (`None`)")
    70	
    71	        elif where is Ellipsis:
    72	            raise IndexError("scalar Record cannot be sliced by an ellipsis (`...`)")
    73	
    74	        elif isinstance(where, tuple):
    75	            raise NotImplementedError("needs _getitem_next")
    76	
    77	        elif isinstance(where, ak.highlevel.Array):
    78	            raise IndexError("scalar Record cannot be sliced by an array")
    79	
    80	        elif isinstance(where, Content):
Here's the content of /repo/tests/test_0912-packed.py with line numbers:
     1	# BSD 3-Clause License; see https://github.com/scikit-hep/awkward-1.0/blob/main/LICENSE
     2	
     3	from __future__ import absolute_import
     4	
     5	import pytest  # noqa: F401
     6	import numpy as np  # noqa: F401
     7	import awkward as ak  # noqa: F401
     8	
     9	
    10	def test_numpy_array():
    11	    matrix = np.arange(64).reshape(8, -1)
    12	    layout = ak.layout.NumpyArray(matrix[:, 0])
    13	    assert not layout.iscontiguous
    14	
    15	    packed = ak.packed(layout, highlevel=False)
    16	    assert ak.to_list(packed) == ak.to_list(layout)
    17	    assert packed.iscontiguous
    18	
    19	
    20	def test_empty_array():
    21	    layout = ak.layout.EmptyArray()
    22	    assert ak.packed(layout, highlevel=False) is layout
    23	
    24	
    25	def test_indexed_option_array():
    26	    index = ak.layout.Index64(np.r_[0, -1, 2, -1, 4])
    27	    content = ak.layout.NumpyArray(np.arange(8))
    28	    layout = ak.layout.IndexedOptionArray64(index, content)
    29	
    30	    packed = ak.packed(layout, highlevel=False)
    31	    assert ak.to_list(layout) == ak.to_list(packed)
    32	    assert isinstance(packed, ak.layout.IndexedOptionArray64)
    33	    assert np.asarray(packed.index).tolist() == [0, -1, 1, -1, 2]
    34	    assert len(packed.content) == 3
    35	
    36	
    37	def test_indexed_array():
    38	    index = ak.layout.Index64(np.array([0, 1, 2, 3, 6, 7, 8]))
    39	    content = ak.layout.NumpyArray(np.arange(10))
    40	    layout = ak.layout.IndexedArray64(index, content)
    41	
    42	    packed = ak.packed(layout, highlevel=False)
    43	    assert ak.to_list(packed) == ak.to_list(layout)
    44	
    45	    assert isinstance(packed, ak.layout.NumpyArray)
    46	    assert len(packed) == len(index)
    47	
    48	
    49	def test_list_array():
    50	    content = ak.layout.NumpyArray(
    51	        np.array([1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9])
    52	    )
    53	    starts = ak.layout.Index64(np.array([0, 3, 3, 5, 6]))
    54	    stops = ak.layout.Index64(np.array([3, 3, 5, 6, 9]))
    55	    layout = ak.layout.ListArray64(starts, stops, content)
    56	
    57	    packed = ak.packed(layout, highlevel=False)
    58	    assert ak.to_list(packed) == ak.to_list(layout)
    59	    assert isinstance(packed, ak.layout.ListOffsetArray64)
    60	    assert packed.offsets[0] == 0
    61	
    62	
    63	def test_list_offset_array():
    64	    content = ak.layout.NumpyArray(
    65	        np.array([1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9])
    66	    )
    67	    offsets = ak.layout.Index64(np.array([0, 3, 3, 5, 6]))
    68	    layout = ak.layout.ListOffsetArray64(offsets, content)
    69	
    70	    packed = ak.packed(layout, highlevel=False)
    71	    assert ak.to_list(packed) == ak.to_list(layout)
    72	    assert isinstance(packed, ak.layout.ListOffsetArray64)
    73	    assert packed.offsets[0] == 0
    74	    assert len(packed.content) == packed.offsets[-1]
    75	
    76	
    77	def test_unmasked_array():
    78	    content = ak.layout.NumpyArray(
    79	        np.array([1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9])
    80	    )
    81	    layout = ak.layout.UnmaskedArray(content)
    82	    packed = ak.packed(layout, highlevel=False)
    83	    assert ak.to_list(packed) == ak.to_list(layout)
    84	
    85	
    86	def test_union_array():
    87	    a = ak.layout.NumpyArray(np.arange(4))
    88	    b = ak.layout.NumpyArray(np.arange(4) + 4)
    89	    c = ak.layout.RegularArray(ak.layout.NumpyArray(np.arange(12)), 3)
    90	    layout = ak.layout.UnionArray8_64(
    91	        ak.layout.Index8([1, 1, 2, 2, 0, 0]),
    92	        ak.layout.Index64([0, 1, 0, 1, 0, 1]),
    93	        [a, b, c],
    94	    )
    95	    packed = ak.packed(layout, highlevel=False)
    96	    assert ak.to_list(packed) == ak.to_list(layout)
    97	    # Check that it merges like contents
    98	    assert len(packed.contents) == 2
    99	    index_0 = np.asarray(packed.index)[np.asarray(packed.tags) == 0]
   100	    assert index_0.tolist() == [0, 1, 2, 3]
   101	
   102	
   103	def test_record_array():
   104	    a = ak.layout.NumpyArray(np.arange(10))
   105	    b = ak.layout.NumpyArray(np.arange(10) * 2 + 4)
   106	    layout = ak.layout.RecordArray([a, b], None, 5)
   107	    packed = ak.packed(layout, highlevel=False)
   108	    assert ak.to_list(packed) == ak.to_list(layout)
   109	    assert len(packed.contents[0]) == 5
   110	    assert len(packed.contents[1]) == 5
   111	
   112	
   113	def test_regular_array():
   114	    content = ak.layout.NumpyArray(np.arange(10))
   115	    layout = ak.layout.RegularArray(content, 3)
   116	    packed = ak.packed(layout, highlevel=False)
   117	    assert ak.to_list(packed) == ak.to_list(layout)
   118	    assert len(packed.content) == 9
   119	    assert packed.size == layout.size
   120	
   121	
   122	def test_bit_masked_aray():
   123	    mask = ak.layout.IndexU8(np.array([0b10101010]))
   124	    content = ak.layout.NumpyArray(np.arange(16))
   125	    layout = ak.layout.BitMaskedArray(mask, content, False, 8, False)
   126	    packed = ak.packed(layout, highlevel=False)
   127	    assert ak.to_list(packed) == ak.to_list(layout)
   128	    assert len(packed.content) == 8
   129	
   130	
   131	def test_byte_masked_array():
   132	    mask = ak.layout.Index8(np.array([1, 0, 1, 0, 1, 0, 1, 0]))
   133	    content = ak.layout.NumpyArray(np.arange(16))
   134	    layout = ak.layout.ByteMaskedArray(
   135	        mask,
   136	        content,
   137	        False,
   138	    )
   139	    packed = ak.packed(layout, highlevel=False)
   140	    assert ak.to_list(packed) == ak.to_list(layout)
   141	    assert len(packed.content) == 8
   142	
   143	
   144	def test_virtual_array():
   145	    n_called = [0]
   146	
   147	    def generate():
   148	        n_called[0] += 1
   149	        return ak.layout.NumpyArray(np.array([1.1, 2.2, 3.3, 4.4, 5.5]))
   150	
   151	    generator = ak.layout.ArrayGenerator(
   152	        generate, form=ak.forms.NumpyForm([], 8, "d"), length=5
   153	    )
   154	    layout = ak.layout.VirtualArray(generator)
   155	    assert n_called[0] == 0
   156	    packed = ak.packed(layout, highlevel=False)
   157	    assert n_called[0] == 1
   158	
   159	    assert isinstance(packed, ak.layout.NumpyArray)
   160	    assert ak.to_list(packed) == ak.to_list(layout)
   161	
   162	
   163	def test_partitioned_array():
   164	    index_0 = ak.layout.Index64(np.array([0, 1, 2, 3, 6, 7, 8]))
   165	    content_0 = ak.layout.NumpyArray(np.arange(10))
   166	    content = ak.layout.IndexedArray64(index_0, content_0)
   167	    layout = ak.partitioned([content, content], highlevel=False)
   168	    packed = ak.packed(layout, highlevel=False)
   169	
   170	    assert ak.to_list(layout) == ak.to_list(packed)
   171	    assert isinstance(packed, ak.partition.PartitionedArray)
   172	
   173	    assert isinstance(packed.partitions[0], ak.layout.NumpyArray)
   174	    assert len(packed.partitions[0]) == len(index_0)
   175	
   176	    assert isinstance(packed.partitions[1], ak.layout.NumpyArray)
   177	    assert len(packed.partitions[1]) == len(index_0)
   178	
   179	
   180	def test_record():
   181	    a = ak.layout.NumpyArray(np.arange(10))
   182	    b = ak.layout.NumpyArray(np.arange(10) * 2 + 4)
   183	    layout = ak.layout.RecordArray([a, b], None, 5)
   184	    first = layout[0]
   185	    packed = ak.packed(first, highlevel=False)
   186	    assert ak.to_list(packed) == ak.to_list(first)
   187	    assert len(packed.array) == len(layout)
   188
504:def maybe_wrap_like(content, array, behavior, highlevel):
Here's the content of /repo/src/awkward/_util.py with line numbers (which has a total of 1894 lines) with view_range=[504, 550]:
   504	def maybe_wrap_like(content, array, behavior, highlevel):
   505	    return maybe_wrap(content, behaviorof(array, behavior=behavior), highlevel)
   506	
   507	
   508	def extra(args, kwargs, defaults):
   509	    out = []
   510	    for i in range(len(defaults)):
   511	        name, default = defaults[i]
   512	        if i < len(args):
   513	            out.append(args[i])
   514	        elif name in kwargs:
   515	            out.append(kwargs[name])
   516	        else:
   517	            out.append(default)
   518	    return out
   519	
   520	
   521	def key2index(keys, key):
   522	    if keys is None:
   523	        attempt = None
   524	    else:
   525	        try:
   526	            attempt = keys.index(key)
   527	        except ValueError:
   528	            attempt = None
   529	
   530	    if attempt is None:
   531	        m = key2index._pattern.match(key)
   532	        if m is not None:
   533	            attempt = m.group(0)
   534	
   535	    if attempt is None:
   536	        raise ValueError(
   537	            "key {0} not found in record".format(repr(key)) + exception_suffix(__file__)
   538	        )
   539	    else:
   540	        return attempt
   541	
   542	
   543	key2index._pattern = re.compile(r"^[1-9][0-9]*$")
   544	
   545	
   546	def completely_flatten(array):
   547	    if isinstance(array, ak.partition.PartitionedArray):
   548	        out = []
   549	        for partition in array.partitions:
   550	            for outi in completely_flatten(partition):
497:def maybe_wrap(content, behavior, highlevel):
504:def maybe_wrap_like(content, array, behavior, highlevel):
1752:    def maybe_wrap(cls, mapping):
Here's the content of /repo/src/awkward/_util.py with line numbers (which has a total of 1894 lines) with view_range=[497, 506]:
   497	def maybe_wrap(content, behavior, highlevel):
   498	    if highlevel:
   499	        return ak._util.wrap(content, behavior)
   500	    else:
   501	        return content
   502	
   503	
   504	def maybe_wrap_like(content, array, behavior, highlevel):
   505	    return maybe_wrap(content, behaviorof(array, behavior=behavior), highlevel)
   506
Tool ran without output or errors
Tool ran without output or errors
elif isinstance(layout, ak.layout.Record):
        return layout
elif isinstance(layout, ak.layout.Record):
        return ak.layout.Record(
            layout.array[layout.at : layout.at + 1], 0
        )
def test_record():
    a = ak.layout.NumpyArray(np.arange(10))
    b = ak.layout.NumpyArray(np.arange(10) * 2 + 4)
    layout = ak.layout.RecordArray([a, b], None, 5)
    first = layout[0]
    packed = ak.packed(first, highlevel=False)
    assert ak.to_list(packed) == ak.to_list(first)
    assert len(packed.array) == len(layout)
Here's the content of /repo/src/awkward/operations/structure.py with line numbers (which has a total of 4645 lines) with view_range=[2320, 2340]:
  2320	    elif isinstance(layout, ak.layout.VirtualArray):
  2321	        return layout.array
  2322	
  2323	    elif isinstance(layout, ak.partition.PartitionedArray):
  2324	        return layout
  2325	
  2326	    elif isinstance(layout, ak.layout.Record):
  2327	        return ak.layout.Record(
  2328	            layout.array[layout.at : layout.at + 1], 0
  2329	        )
  2330	
  2331	    # Finally, fall through to failure
  2332	    else:
  2333	        raise AssertionError(
  2334	            "unrecognized layout: " + repr(layout) + ak._util.exception_suffix(__file__)
  2335	        )
  2336	
  2337	
  2338	def packed(array, highlevel=True, behavior=None):
  2339	    """
  2340	    Args:
Here's the content of /repo/tests/test_0912-packed.py with line numbers (which has a total of 188 lines) with view_range=[180, 188]:
   180	def test_record():
   181	    a = ak.layout.NumpyArray(np.arange(10))
   182	    b = ak.layout.NumpyArray(np.arange(10) * 2 + 4)
   183	    layout = ak.layout.RecordArray([a, b], None, 5)
   184	    first = layout[0]
   185	    packed = ak.packed(first, highlevel=False)
   186	    assert ak.to_list(packed) == ak.to_list(first)
   187	    assert len(packed.array) == 1
   188
Here's the content of /repo/src/awkward/operations/structure.py with line numbers (which has a total of 4645 lines) with view_range=[2020, 2065]:
  2020	                raise ValueError(
  2021	                    "structure imposed by 'counts' does not fit in the array or partition "
  2022	                    "at axis={0}".format(axis) + ak._util.exception_suffix(__file__)
  2023	                )
  2024	
  2025	            offsets = current_offsets[0][: position + 1]
  2026	            current_offsets[0] = current_offsets[0][position:] - len(layout)
  2027	
  2028	            out = ak.layout.ListOffsetArray64(ak.layout.Index64(offsets), layout)
  2029	            if not isinstance(mask, (bool, np.bool_)):
  2030	                index = ak.layout.Index8(nplike.asarray(mask).astype(np.int8))
  2031	                out = ak.layout.ByteMaskedArray(index, out, valid_when=False)
  2032	
  2033	        return out
  2034	
  2035	    if axis == 0 or layout.axis_wrap_if_negative(axis) == 0:
  2036	        if isinstance(layout, ak.partition.PartitionedArray):
  2037	            outparts = []
  2038	            for part in layout.partitions:
  2039	                outparts.append(doit(part))
  2040	            out = ak.partition.IrregularlyPartitionedArray(outparts)
  2041	        else:
  2042	            out = doit(layout)
  2043	
  2044	    else:
  2045	
  2046	        def transform(layout, depth, posaxis):
  2047	            # Pack the current layout. This ensures that the `counts` array,
  2048	            # which is computed with these layouts applied, aligns with the
  2049	            # internal layout to be unflattened (#910)
  2050	            layout = _pack_layout(layout)
  2051	
  2052	            posaxis = layout.axis_wrap_if_negative(posaxis)
  2053	            if posaxis == depth and isinstance(layout, ak._util.listtypes):
  2054	                # We are one *above* the level where we want to apply this.
  2055	                listoffsetarray = layout.toListOffsetArray64(True)
  2056	                outeroffsets = nplike.asarray(listoffsetarray.offsets)
  2057	
  2058	                content = doit(listoffsetarray.content[: outeroffsets[-1]])
  2059	                if isinstance(content, ak.layout.ByteMaskedArray):
  2060	                    inneroffsets = nplike.asarray(content.content.offsets)
  2061	                elif isinstance(content, ak.layout.RegularArray):
  2062	                    inneroffsets = nplike.asarray(
  2063	                        content.toListOffsetArray64(True).offsets
  2064	                    )
  2065	                else:
Here's the content of /repo/tests/test_1006-packed-regular-array-zero-size.py with line numbers:
     1	# BSD 3-Clause License; see https://github.com/scikit-hep/awkward-1.0/blob/main/LICENSE
     2	
     3	from __future__ import absolute_import
     4	
     5	import pytest  # noqa: F401
     6	import numpy as np  # noqa: F401
     7	import awkward as ak  # noqa: F401
     8	
     9	
    10	def test():
    11	    array = ak.from_numpy(np.zeros((1, 0), dtype=np.int32), regulararray=True)
    12	    packed = ak.packed(array)
    13	    assert ak.to_list(packed) == [[]]
    14
Tool ran without output or errors
Tool ran without output or errors
1835:def to_layout(
Here's the content of /repo/src/awkward/operations/convert.py with line numbers (which has a total of 5394 lines) with view_range=[1835, 1900]:
  1835	def to_layout(
  1836	    array,
  1837	    allow_record=True,
  1838	    allow_other=False,
  1839	    numpytype=(np.number, np.bool_, np.str_, np.bytes_, np.datetime64, np.timedelta64),
  1840	):
  1841	    """
  1842	    Args:
  1843	        array: Data to convert into an #ak.layout.Content and maybe
  1844	            #ak.layout.Record and other types.
  1845	        allow_record (bool): If True, allow #ak.layout.Record as an output;
  1846	            otherwise, if the output would be a scalar record, raise an error.
  1847	        allow_other (bool): If True, allow non-Awkward outputs; otherwise,
  1848	            if the output would be another type, raise an error.
  1849	        numpytype (tuple of NumPy types): Allowed NumPy types in
  1850	            #ak.layout.NumpyArray outputs.
  1851	
  1852	    Converts `array` (many types supported, including all Awkward Arrays and
  1853	    Records) into a #ak.layout.Content and maybe #ak.layout.Record and other
  1854	    types.
  1855	
  1856	    This function is usually used to sanitize inputs for other functions; it
  1857	    would rarely be used in a data analysis.
  1858	    """
  1859	    if isinstance(array, ak.highlevel.Array):
  1860	        return array.layout
  1861	
  1862	    elif allow_record and isinstance(array, ak.highlevel.Record):
  1863	        return array.layout
  1864	
  1865	    elif isinstance(array, ak.highlevel.ArrayBuilder):
  1866	        return array.snapshot().layout
  1867	
  1868	    elif isinstance(array, ak.layout.ArrayBuilder):
  1869	        return array.snapshot()
  1870	
  1871	    elif isinstance(array, (ak.layout.Content, ak.partition.PartitionedArray)):
  1872	        return array
  1873	
  1874	    elif allow_record and isinstance(array, ak.layout.Record):
  1875	        return array
  1876	
  1877	    elif isinstance(array, (np.ndarray, numpy.ma.MaskedArray)):
  1878	        if not issubclass(array.dtype.type, numpytype):
  1879	            raise ValueError(
  1880	                "NumPy {0} not allowed".format(repr(array.dtype))
  1881	                + ak._util.exception_suffix(__file__)
  1882	            )
  1883	        return from_numpy(array, regulararray=True, recordarray=True, highlevel=False)
  1884	
  1885	    elif (
  1886	        type(array).__module__.startswith("cupy.") and type(array).__name__ == "ndarray"
  1887	    ):
  1888	        return from_cupy(array, regulararray=True, highlevel=False)
  1889	
  1890	    elif isinstance(array, (str, bytes)) or (
  1891	        ak._util.py27 and isinstance(array, ak._util.unicode)
  1892	    ):
  1893	        return from_iter([array], highlevel=False)
  1894	
  1895	    elif isinstance(array, Iterable):
  1896	        return from_iter(array, highlevel=False)
  1897	
  1898	    elif not allow_other:
  1899	        raise TypeError(
  1900	            "{0} cannot be converted into an Awkward Array".format(array)
486:def wrap(content, behavior):
Here's the content of /repo/src/awkward/_util.py with line numbers (which has a total of 1894 lines) with view_range=[486, 506]:
   486	def wrap(content, behavior):
   487	    if isinstance(content, (ak.layout.Content, ak.partition.PartitionedArray)):
   488	        return ak.highlevel.Array(content, behavior=behavior, kernels=None)
   489	
   490	    elif isinstance(content, ak.layout.Record):
   491	        return ak.highlevel.Record(content, behavior=behavior, kernels=None)
   492	
   493	    else:
   494	        return content
   495	
   496	
   497	def maybe_wrap(content, behavior, highlevel):
   498	    if highlevel:
   499	        return ak._util.wrap(content, behavior)
   500	    else:
   501	        return content
   502	
   503	
   504	def maybe_wrap_like(content, array, behavior, highlevel):
   505	    return maybe_wrap(content, behaviorof(array, behavior=behavior), highlevel)
   506
Tool ran without output or errors
1529:        layout = layout.array[layout.at : layout.at + 1]
Here's the content of /repo/src/awkward/operations/structure.py with line numbers (which has a total of 4645 lines) with view_range=[2256, 2332]:
  2256	    # RecordArray contents can be truncated
  2257	    elif isinstance(layout, ak.layout.RecordArray):
  2258	        return ak.layout.RecordArray(
  2259	            [c[: len(layout)] for c in layout.contents],
  2260	            layout.recordlookup,
  2261	            len(layout),
  2262	            layout.identities,
  2263	            layout.parameters,
  2264	        )
  2265	
  2266	    # RegularArrays can change length
  2267	    elif isinstance(layout, ak.layout.RegularArray):
  2268	        if not len(layout):
  2269	            return layout
  2270	
  2271	        content = layout.content
  2272	
  2273	        # Truncate content to perfect multiple of the RegularArray size
  2274	        if layout.size > 0:
  2275	            r = len(content) % layout.size
  2276	            content = content[: len(content) - r]
  2277	        else:
  2278	            content = content[:0]
  2279	
  2280	        return ak.layout.RegularArray(
  2281	            content,
  2282	            layout.size,
  2283	            len(layout),
  2284	            layout.identities,
  2285	            layout.parameters,
  2286	        )
  2287	
  2288	    # BitMaskedArrays can change length
  2289	    elif isinstance(layout, ak.layout.BitMaskedArray):
  2290	        layout = layout.simplify()
  2291	
  2292	        if not isinstance(ak.type(layout.content), ak.types.PrimitiveType):
  2293	            return layout.toIndexedOptionArray64()
  2294	
  2295	        return ak.layout.BitMaskedArray(
  2296	            layout.mask,
  2297	            layout.content[: len(layout)],
  2298	            layout.valid_when,
  2299	            len(layout),
  2300	            layout.lsb_order,
  2301	            layout.identities,
  2302	            layout.parameters,
  2303	        )
  2304	
  2305	    # ByteMaskedArrays can change length
  2306	    elif isinstance(layout, ak.layout.ByteMaskedArray):
  2307	        layout = layout.simplify()
  2308	
  2309	        if not isinstance(ak.type(layout.content), ak.types.PrimitiveType):
  2310	            return layout.toIndexedOptionArray64()
  2311	
  2312	        return ak.layout.ByteMaskedArray(
  2313	            layout.mask,
  2314	            layout.content[: len(layout)],
  2315	            layout.valid_when,
  2316	            layout.identities,
  2317	            layout.parameters,
  2318	        )
  2319	
  2320	    elif isinstance(layout, ak.layout.VirtualArray):
  2321	        return layout.array
  2322	
  2323	    elif isinstance(layout, ak.partition.PartitionedArray):
  2324	        return layout
  2325	
  2326	    elif isinstance(layout, ak.layout.Record):
  2327	        return ak.layout.Record(
  2328	            layout.array[layout.at : layout.at + 1], 0
  2329	        )
  2330	
  2331	    # Finally, fall through to failure
  2332	    else:
Here's the content of /repo/tests/test_0912-packed.py with line numbers (which has a total of 188 lines) with view_range=[180, 188]:
   180	def test_record():
   181	    a = ak.layout.NumpyArray(np.arange(10))
   182	    b = ak.layout.NumpyArray(np.arange(10) * 2 + 4)
   183	    layout = ak.layout.RecordArray([a, b], None, 5)
   184	    first = layout[0]
   185	    packed = ak.packed(first, highlevel=False)
   186	    assert ak.to_list(packed) == ak.to_list(first)
   187	    assert len(packed.array) == 1
   188
Tool ran without output or errors
Here're the files and directories up to 2 levels deep in /repo/src/awkward/_v2, excluding hidden items and node_modules:
153K	/repo/src/awkward/_v2
512	/repo/src/awkward/_v2/__init__.py
61K	/repo/src/awkward/_v2/contents
1.5K	/repo/src/awkward/_v2/contents/__init__.py
6.5K	/repo/src/awkward/_v2/contents/bitmaskedarray.py
4.0K	/repo/src/awkward/_v2/contents/bytemaskedarray.py
6.5K	/repo/src/awkward/_v2/contents/content.py
1.5K	/repo/src/awkward/_v2/contents/emptyarray.py
3.0K	/repo/src/awkward/_v2/contents/indexedarray.py
3.0K	/repo/src/awkward/_v2/contents/indexedoptionarray.py
4.0K	/repo/src/awkward/_v2/contents/listarray.py
3.5K	/repo/src/awkward/_v2/contents/listoffsetarray.py
4.0K	/repo/src/awkward/_v2/contents/numpyarray.py
8.5K	/repo/src/awkward/_v2/contents/recordarray.py
4.5K	/repo/src/awkward/_v2/contents/regulararray.py
4.5K	/repo/src/awkward/_v2/contents/unionarray.py
2.0K	/repo/src/awkward/_v2/contents/unmaskedarray.py
37K	/repo/src/awkward/_v2/forms
1.5K	/repo/src/awkward/_v2/forms/__init__.py
2.5K	/repo/src/awkward/_v2/forms/bitmaskedform.py
2.0K	/repo/src/awkward/_v2/forms/bytemaskedform.py
1.0K	/repo/src/awkward/_v2/forms/emptyform.py
8.0K	/repo/src/awkward/_v2/forms/form.py
2.0K	/repo/src/awkward/_v2/forms/indexedform.py
2.0K	/repo/src/awkward/_v2/forms/indexedoptionform.py
2.0K	/repo/src/awkward/_v2/forms/listform.py
1.5K	/repo/src/awkward/_v2/forms/listoffsetform.py
3.5K	/repo/src/awkward/_v2/forms/numpyform.py
2.5K	/repo/src/awkward/_v2/forms/recordform.py
1.5K	/repo/src/awkward/_v2/forms/regularform.py
2.5K	/repo/src/awkward/_v2/forms/unionform.py
1.5K	/repo/src/awkward/_v2/forms/unmaskedform.py
2.0K	/repo/src/awkward/_v2/forms/virtualform.py
3.5K	/repo/src/awkward/_v2/identifier.py
4.5K	/repo/src/awkward/_v2/index.py
3.5K	/repo/src/awkward/_v2/record.py
16K	/repo/src/awkward/_v2/tmp_for_testing.py
24K	/repo/src/awkward/_v2/types
1.0K	/repo/src/awkward/_v2/types/__init__.py
1.5K	/repo/src/awkward/_v2/types/arraytype.py
2.0K	/repo/src/awkward/_v2/types/listtype.py
4.0K	/repo/src/awkward/_v2/types/numpytype.py
2.5K	/repo/src/awkward/_v2/types/optiontype.py
4.0K	/repo/src/awkward/_v2/types/recordtype.py
2.5K	/repo/src/awkward/_v2/types/regulartype.py
2.0K	/repo/src/awkward/_v2/types/type.py
2.5K	/repo/src/awkward/_v2/types/uniontype.py
1.5K	/repo/src/awkward/_v2/types/unknowntype.py
elif isinstance(layout, ak.layout.Record):
    return layout
elif isinstance(layout, ak.layout.Record):
    return ak.layout.Record(
        layout.array[layout.at : layout.at + 1], 0
    )
