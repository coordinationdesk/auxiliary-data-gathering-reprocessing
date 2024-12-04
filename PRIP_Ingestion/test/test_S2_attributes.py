import os
import unittest

from ..ingestion.lib.attributes import get_attributes

s2_data_files = {
    'S2_MPL_ORBRES': 'S2A_OPER_MPL_ORBRES_20240405T030300_20240415T030300_0001.EOF.zip',
    #'S2_MPL_ORBPRE': 'S2B_OPER_MPL_ORBPRE_20240318T030421_20240328T030421_0001.EOF.zip',
    #'S2_REP_SUP': 'S2A_OPER_REP__SUP___20230324T131500_99999999T999999_0001.EOF.zip',
    # 'S2_AUX_SADATA_EOF': '',
    #'S2_AUX_EOF_Error': '',
    'S2_GIP_L2A_XML': 'S2__OPER_GIP_L2ACFG_MPC__20230801T114500_V20150622T000000_21000101T000000_B00.TGZ',
    # 'S2_GIP_OLQCPA_XML': '',
    'S2_AUX_ECMWFD': 'S2__OPER_AUX_ECMWFD_ADG__20240116T000000_V20240116T090000_20240118T030000.TGZ',
    # 'S2_AUX_CAMS': '',
    'S2_MAN_PRE_file': 'S2B_OPER_MPL_MANPRE_20220712T125143_20220714T064944_0001.DBL.zip',
    # 'S2_HDR_Folder': '',
    'S2_HDR_No_Folder': 'S2A_OPER_GIP_R2ABCA_MPC__20180712T132200_V20180716T010000_21000101T000000_B00.TGZ'
}

class TestS2Attributes(unittest.TestCase):
    data_path = 'PRIP_Ingestion/test/test_data'
    # Test HDR
    # Test HDR No Folder
    # TE MANPRE
    # TLMREQ
    # L2CFG
    # Other file not found products
    def test_MANPRE_attributes(self):
        prod_file_path = os.path.join(self.data_path, s2_data_files.get('S2_MANPRE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '2017-10-03T12:07:30.000000')
        self.assertEqual(attrs.get("productType"), 'MCSF')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'CLS-Brest')
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_L2A_CFG_attribtues(self):
        prod_file_path = os.path.join(self.data_path, s2_data_files.get('S2_GIP_L2A_XML'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2023-08-01T11:45:00')
        self.assertEqual(attrs.get("productType"), 'GIP_L2ACFG')  # add assertion here
        self.assertEqual(attrs.get("processingCenter"), 'MPC_')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_EOF_attributes(self):
        prod_file_path = os.path.join(self.data_path, s2_data_files.get('S2_MPL_ORBRES'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2024-04-08T03:02:56')
        self.assertEqual(attrs.get("productType"), 'MPL_ORBRES')  # add assertion here
        self.assertEqual(attrs.get("processingCenter"), 'FOS')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_ECMWFD_attributes(self):
        prod_file_path = os.path.join(self.data_path, s2_data_files.get('S2_AUX_ECMWFD'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2024-01-16T00:00:00')
        self.assertEqual(attrs.get("productType"), 'AUX_ECMWFD')  # add assertion here
        self.assertEqual(attrs.get("processingCenter"), 'ADG_')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    '''
    def test_HDR_attributes(self):
        prod_file_path = os.path.join(self.data_path, s2_data_files.get('S1_EOF_file'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2024-05-02T07:07:57')
        self.assertEqual(attrs.get("productType"), 'AUX_POEORB')  # add assertion here
        self.assertEqual(attrs.get("processingCenter"), 'OPOD')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")
    '''

    def test_HDR_NoFolder_attributes(self):
        prod_file_path = os.path.join(self.data_path, s2_data_files.get('S2_HDR_No_Folder'))
        attrs = get_attributes(prod_file_path)
        self.assertIsNotNone(attrs)
        self.assertEqual(attrs.get('processingDate'), '2018-07-12T13:22:00')
        self.assertEqual(attrs.get("productType"), 'GIP_R2ABCA')  # add assertion here
        self.assertEqual(attrs.get("processingCenter"), 'MPC_')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")


if __name__ == '__main__':
    unittest.main()
