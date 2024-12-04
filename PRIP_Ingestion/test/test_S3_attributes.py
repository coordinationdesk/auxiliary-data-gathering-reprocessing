import os
import unittest
from ..ingestion.lib.attributes import get_attributes


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
