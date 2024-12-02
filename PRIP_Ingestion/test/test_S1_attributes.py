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
    'S1_REP_MP': '',
    'S1_TLEPRE_file': '',
    'S1_MANPRE_file': '',
}
s2_data_files = {
    'S2_MPL_ORBRES': 'S2A_OPER_MPL_ORBRES_20240405T030300_20240415T030300_0001.EOF.zip',
    'S2_MPL_ORBPRE': 'S2B_OPER_MPL_ORBPRE_20240318T030421_20240328T030421_0001.EOF.zip',
    'S2_REP_SUP': 'S2A_OPER_REP__SUP___20230324T131500_99999999T999999_0001.EOF.zip',
    'S2_AUX_SADATA_EOF': '',
    'S2_AUX_EOF_Error': '',
    'S2_GIP_L2A_XML': '',
    'S2_GIP_OLQCPA_XML': '',
    'S2_AUX_ECMWFD': '',
    'S2_AUX_CAMS': '',

}

# SL_1_VSC_AX, SR_2_SIC_AX, AX___FRO_AX, SR___POESAX, SR___POEPAX
# MW_1_DNB_AX, SR_1_CA2KAX, MW_1_NIR_AX
# AX___MF2_AX, SR___MDO_AX
# SR_2_PMPPAX, GN_1_MANHAX, AUX_GNSSRD
s3_data_files = {
    'S3_VSC_file': 'S3B_SL_1_VSC_AX_20201228T191445_20500101T000000_20201228T213335___________________LN2_O_NN____.SEN3.zip',
#    'S3_SIC_file': '',
    'S3_FRO_file': 'S3B_AX___FRO_AX_20231116T000000_20231126T000000_20231119T065357___________________EUM_O_AL_001.SEN3.zip',
    'S3_POE_file': 'S3A_SR___POEPAX_20210410T215942_20210411T235942_20210506T072935___________________POD_O_NT_001.SEN3.zip',
#    'S3_MDO_file': '',
    'S3_MA2_file': 'S3__AX___MA2_AX_20240803T090000_20240803T210000_20240803T174656___________________ECW_O_SN_001.SEN3.zip',
    'S3_MW_1_DNB_file': 'S3A_MW_1_DNB_AX_20000101T000000_20201129T005440_20201129T011540___________________LN3_O_AL____.SEN3.zip',
    'S3_USO_file': 'S3B_SR_1_USO_AX_20180501T144459_20210329T022843_20210329T084851___________________CNE_O_AL_001.SEN3.zip',
    'S3_MW_1_NIR_file': 'S3A_MW_1_NIR_AX_20000101T000000_20201128T195026_20201128T201332___________________LN3_O_AL____.SEN3.zip',
    #'S3_PMP_file': '',
#    'S3_GNSSRD_file': '',
#    'S3_GN_!_MANHAX_file': '',
#    'S3_SAFE_file': ''
}


class TestS1Attributes(unittest.TestCase):
    data_path = 'PRIP_Ingestion/test/test_data'

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
        self.assertEqual('2024-08-13T04:32:51.061935', attrs.get('processingDate') )
        self.assertEqual('AUX_WAV', attrs.get("productType"))  # add assertion here
        self.assertEqual('PDMC', attrs.get('processingCenter'))
        # TODO Test reading Date attributes
        # Check  end date is 1 day after start date

    def test_WND_SAFE_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_WND_file'))
        attrs = get_attributes(prod_file_path)
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
        self.assertEqual(attrs.get('processingDate'), '2021-05-06T04:00:09')
        self.assertEqual(attrs.get("productType"), 'AMH_ERRMAT')  # add assertion here
        self.assertEqual(attrs.get("endingDateTime"), '2021-05-05T11:33:57')

    def test_AUX_PP1_attributes(self):
        prod_file_path = os.path.join(self.data_path, s1_data_files.get('S1_AUX_PP1_SAFE_file'))
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '2017-10-03T12:07:30.000000')
        self.assertEqual(attrs.get("productType"), 'AUX_PP1')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'CLS-Brest')


class TestS2Attributes(unittest.TestCase):
    data_path = 'test_data'


class TestS3Attributes(unittest.TestCase):
    data_path = 'PRIP_Ingestion/test/test_data'
    def test_MW_1_DNB_attributes(self):
        prod_file_path = os.path.join(self.data_path, s3_data_files.get('S3_MW_1_DNB_file'))
        self.assertIsNotNone(prod_file_path)
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '20201129T011540')
        self.assertEqual(attrs.get("productType"), 'MW_1_DNB_AX')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'Toulouse')
        self.assertEqual(attrs.get('timeliness'), 'AL')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_VSC_attributes(self):
        prod_file_path = os.path.join(self.data_path, s3_data_files.get('S3_VSC_file'))
        self.assertIsNotNone(prod_file_path)
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '20201228T213335')
        self.assertEqual(attrs.get("productType"), 'SL_1_VSC_AX')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'Cloud Service Provider')  # Darmstadt
        self.assertEqual(attrs.get('timeliness'), 'NN')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_FRO_attributes(self):
        prod_file_path = os.path.join(self.data_path, s3_data_files.get('S3_FRO_file'))
        self.assertIsNotNone(prod_file_path)
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '20231119T065357')
        self.assertEqual(attrs.get("productType"), 'AX___FRO_AX')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'Darmstadt')
        self.assertEqual(attrs.get('timeliness'), 'AL')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_MW_1_NIR_attributes(self):
        prod_file_path = os.path.join(self.data_path, s3_data_files.get('S3_MW_1_NIR_file'))
        self.assertIsNotNone(prod_file_path)
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '20201128T201332')
        self.assertEqual(attrs.get("productType"), 'MW_1_NIR_AX')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'Toulouse')
        self.assertEqual(attrs.get('timeliness'), 'AL')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_USO_attributes(self):
        prod_file_path = os.path.join(self.data_path, s3_data_files.get('S3_USO_file'))
        self.assertIsNotNone(prod_file_path)
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '20210329T084851')
        self.assertEqual(attrs.get("productType"), 'SR_1_USO_AX')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'Darmstadt')
        self.assertEqual(attrs.get('timeliness'), 'AL')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")

    def test_POE_attributes(self):
        prod_file_path = os.path.join(self.data_path, s3_data_files.get('S3_POE_file'))
        self.assertIsNotNone(prod_file_path)
        attrs = get_attributes(prod_file_path)
        self.assertEqual(attrs.get('processingDate'), '20210506T072935')
        self.assertEqual(attrs.get("productType"), 'SR___POEPAX')  # add assertion here
        self.assertEqual(attrs.get('processingCenter'), 'Darmstadt')
        self.assertEqual(attrs.get('timeliness'), 'NT')
        #  check that uncompressed zip is not present
        prod_folder = os.path.splitext(prod_file_path)[0]
        self.assertTrue(not os.path.exists(prod_folder), f"{prod_folder} not deleted")




if __name__ == '__main__':
    unittest.main()
