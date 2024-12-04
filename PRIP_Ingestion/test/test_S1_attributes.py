import unittest
import os
from ..ingestion.lib.attributes import get_attributes

s1_data_files = {
    'S1_AUX_WAV_NCDF_SAFE_file': 'S1__AUX_WAV_V20240811T210000_G20240813T043251.SAFE.zip',
    'S1_AUX_ICE_NCDF_SAFE_file': 'S1__AUX_ICE_V20240429T120000_G20240430T042034.SAFE.zip',
    'S1_AUX_WND_file': 'S1__AUX_WND_V20240503T220000_G20240501T180359.SAFE.zip',
    'S1_EOF_file': 'S1A_OPER_AUX_POEORB_OPOD_20240502T070757_V20240411T225942_20240413T005942.EOF.zip',
    'S1_EOF_file_error': 'S1A_OPER_AUX_POEORB_OPOD_20220212T081613_V20220122T225942_20220124T005942.EOF.zip',
    'S1_AMH_ERRMAT_file': 'S1A_OPER_AMH_ERRMAT_MPC__20210506T040009_V20000101T000000_20210505T113357.EOF.zip',
    'S1_AUX_PP1_SAFE_file': 'S1A_AUX_PP1_V20150519T120000_G20171003T120730.SAFE.zip',
    'S1_SAFE_error_file': 'S1__AUX_WND_V20220121T150000_G20220121T174615.SAFE.zip',
    'S1_MCSF_file': 'S1B_OPER_REP__MCSF__20160429T072531_20221109T131208_0001.TGZ',
    'S1_MACP_file': 'S1B_OPER_REP__MACP__20160429T072531_20220803T222903_0001.TGZ',
    'S1_SMPR_file': 'S1A_OPER_REP__SMPR__20230417T025020_20230417T025020_0369.TGZ',
    'S1_TLEPRE_file': 'S1A_OPER_MPL_TLEPRE_20240505T000000_20240513T000000_0001.TGZ',
    'S1_MANPRE_file': 'S1A_OPER_MPL_MANPRE_20231114T163837_20231115T224848_0001.DBL.zip',
    'S1_MP_PDMC': 'S1A_OPER_REP_MP_MP__PDMC_20220610T070040_V20220610T160000_20220630T180000.xml.zip',
    'S1_TLM_REQ_file': 'S1A_OPER_TLM__REQ_D_20241026T230000_20241028T000000_0001.TGZ'
}


class TestS1Attributes(unittest.TestCase):
    data_path = 'PRIP_Ingestion/test/test_data'
    '''
    def test_ICID_attribute(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_ICE_NCDF_SAFE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('InstrumentConfiguration'), '2')
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_WAV_NCDF_SAFE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('InstrumentConfiguration'), '2')
    '''
    def test_ICE_SAFE_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_ICE_NCDF_SAFE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2024-04-30T04:20:34.756885')
        self.assertEqual(attrs.get("productType"), 'AUX_ICE')  # add assertion here
        self.assertEqual(attrs.get("processingCenter"), 'PDMC')
        # TODO Test reading Date attributes
        # Check  end date is 1 day after start date

    def test_WAV_SAFE_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_WAV_NCDF_SAFE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual('2024-08-13T04:32:51.061935', attrs.get('processingDate') )
        self.assertEqual('AUX_WAV', attrs.get("productType"))  # add assertion here
        self.assertEqual('PDMC', attrs.get('processingCenter'))
        # TODO Test reading Date attributes
        # Check  end date is 1 day after start date

    def test_WND_SAFE_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_WND_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2024-05-01T18:03:59.097102')
        self.assertEqual(attrs.get("productType"), 'AUX_WND')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'PDMC')
        # TODO Test reading Date attributes
        # Check  end date is 1 day after start date

    def test_SAFE_attributes_w_error(self):
        # Error for folder not under zip
        # error for XML not found
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_SAFE_error_file'))
        self.assertRaises(Exception, get_attributes(prod_file_path))

    def test_EOF_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_EOF_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2024-05-02T07:07:57')
        self.assertEqual(attrs.get("productType"), 'AUX_POEORB')  # add assertion here
        self.assertEqual(attrs.get("processingCenter"), 'OPOD')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_EOF_attributes_w_error(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_EOF_file_error'))
        self.assertRaises(Exception, get_attributes(prod_file_path))

    def test_ERRMAT_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AMH_ERRMAT_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2021-05-06T04:00:09')
        self.assertEqual(attrs.get("productType"), 'AMH_ERRMAT')  # add assertion here
        self.assertEqual(attrs.get("endingDateTime"), '2021-05-05T11:33:57')

    def test_AUX_PP1_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_PP1_SAFE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '2017-10-03T12:07:30.000000')
        self.assertEqual(attrs.get("productType"), 'AUX_PP1')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'CLS-Brest')

    def test_MCSF_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_MCSF_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2022-11-10T16:10:27')
        self.assertEqual(attrs.get("productType"), 'REP__MCSF_')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'FOCC')

    def test_MACP_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_MACP_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs, 'Failure getting attributes')
        self.assertEqual(attrs.get('processingDate'), '2022-08-03T09:00:58')
        self.assertEqual(attrs.get("productType"), 'REP__MACP_')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'FOCC')

    def test_SMPR_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_SMPR_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2023-04-17T02:50:20')
        self.assertEqual(attrs.get("productType"), 'REP__SMPR_')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'FOS')

    def test_MANPRE_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_MANPRE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '2023/11/14-16:38:37.118')
        self.assertEqual(attrs.get("productType"), 'MPL_MANPRE')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'S1MPL')
        self.assertEqual('2023/11/15-22:48:48.179', attrs.get('beginningDateTime'))
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_MP_PDMC_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_MP_PDMC'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual('2022-06-10T07:00:40', attrs.get('processingDate'))
        self.assertEqual(attrs.get("productType"), 'REP_MP_MP_')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'S1MPL')
        self.assertEqual('2022-06-10T16:00:00', attrs.get('beginningDateTime'))

    def test_TLM_REQ_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_TLM_REQ_file'))
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '2024-10-26T23:00:00')
        self.assertEqual(attrs.get("productType"), 'TLM__REQ_D')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'FOS')





if __name__ == '__main__':
    unittest.main()
