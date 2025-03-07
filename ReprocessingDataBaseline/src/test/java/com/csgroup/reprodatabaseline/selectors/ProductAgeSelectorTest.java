package com.csgroup.reprodatabaseline.selectors;

import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class ProductAgeSelectorTest {
    private Map<String, Long> maxAgesConfiguration ;
    private ProductAgeSelector ageSelector;
    private Map<String, AuxFile> auxFileRepo;
    @BeforeEach
    void setUp() {
        // FIll configuration
        maxAgesConfiguration = new HashMap<>();
        maxAgesConfiguration.put("AMH_ERRMAT_MPC", 310L);
        maxAgesConfiguration.put("AMV_ERRMAT_MPC", 310L);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        L0Product l0ToCompare = new L0Product();
        l0ToCompare.setName("S1A_IW_RAW__0NDV_20201001T062556_20201001T063833_034599_040733_8B28");
        l0ToCompare.setValidityStart(LocalDateTime.parse("2020-10-01 06:25:56", formatter));
        l0ToCompare.setValidityStop(LocalDateTime.parse("2020-10-02 06:25:56", formatter));
        L0Product.T0T1DateTime t0t1 = l0ToCompare.getLevel0StartStop( "S1");

        ageSelector = new ProductAgeSelector(t0t1, maxAgesConfiguration);

        auxFileRepo = new HashMap<>();
        AuxFile auxfile1 = new AuxFile();
        auxfile1.FullName="S1A_OPER_AMH_ERRMAT_MPC__20220502T040006_V20000101T000000_20220501T041713.EOF.zip";
        auxfile1.AuxType = "AMH_ERRMAT_MPC";
        auxfile1.ValidityStart = ZonedDateTime.parse("2000-01-01T00:00:00Z");
        auxfile1.ValidityStop = ZonedDateTime.parse("2022-05-01T04:17:13Z");
        auxFileRepo.put("AMH_2022", auxfile1);


        AuxFile auxfile2 = new AuxFile();
        auxfile2.FullName="S1A_OPER_AMH_ERRMAT_MPC__20200101T040010_V20000101T000000_20191231T201224.EOF.zip";
        auxfile2.AuxType = "AMH_ERRMAT_MPC";
        auxfile2.ValidityStart = ZonedDateTime.parse("2000-01-01T00:00:00Z");
        auxfile2.ValidityStop = ZonedDateTime.parse("2019-12-31T20:12:24Z");
        auxFileRepo.put("AMH_2019", auxfile2);

        AuxFile auxfile3 = new AuxFile();
        auxfile3.FullName="S1B_OPER_AMV_ERRMAT_MPC__20161230T040024_V20000101T000000_20161229T234420.EOF.zip";
        auxfile3.AuxType = "AMV_ERRMAT_MPC";
        auxfile3.ValidityStart = ZonedDateTime.parse("2000-01-01T00:00:00Z");
        auxfile3.ValidityStop = ZonedDateTime.parse("2016-12-29T23:44:20Z");
        auxFileRepo.put("AMV_2016", auxfile3);
        AuxFile auxfile4 = new AuxFile();
        auxfile4.FullName="S1A_OPER_AMV_ERRMAT_MPC__20210101T040006_V20000101T000000_20201231T203458.EOF.zip";
        auxfile4.AuxType = "AMV_ERRMAT_MPC";
        auxfile4.ValidityStart = ZonedDateTime.parse("2000-01-01T00:00:00Z");
        auxfile4.ValidityStop = ZonedDateTime.parse("2020-12-31T20:34:58Z");
        auxFileRepo.put("AMV_2020", auxfile4);
        AuxFile auxfile5 = new AuxFile();
        auxfile5.FullName="S1A_OPER_AMH_ERRMAT_MPC__20200903T040006_V20000101T000000_20200902T191131.EOF.zip";
        auxfile5.AuxType = "AMH_ERRMAT_MPC";
        auxfile5.ValidityStart = ZonedDateTime.parse("2000-01-01T00:00:00Z");
        auxfile5.ValidityStop = ZonedDateTime.parse("2020-09-02T19:11:31Z");
        auxFileRepo.put("AMV_2020_09", auxfile5);


    }
    @Test
    void selectAuxFileNearProduct() {
        // L0 2020-10-02
        assertDoesNotThrow(()->ageSelector.selectAuxFile(auxFileRepo.get("AMV_2020_09")));
        try {
            assertTrue(ageSelector.selectAuxFile(auxFileRepo.get("AMV_2020_09")));
        }
        catch (Exception ex) {
            System.out.println("Caught exception");;
        }
    }

    @Test
    void selectAuxFileNearAfterProduct() {
        // L0 2020-10-02
        assertDoesNotThrow(()->ageSelector.selectAuxFile(auxFileRepo.get("AMV_2020")));
        try {
            assertTrue(ageSelector.selectAuxFile(auxFileRepo.get("AMV_2020")));
        }
        catch (Exception ex) {
            System.out.println("Caught exception");;
        }
    }
    @Test
    void selectAuxFileAfterProduct() {
        // L0 2020-10-02
        assertDoesNotThrow(()->ageSelector.selectAuxFile(auxFileRepo.get("AMH_2022")));
        try {
            assertFalse(ageSelector.selectAuxFile(auxFileRepo.get("AMH_2022")));
        }
        catch (Exception ex) {
            System.out.println("Caught exception");;
        }
    }
    @Test
    void selectAuxFilesFarFromProduct() {
        // L0 2020-10-02
        assertDoesNotThrow(()->ageSelector.selectAuxFile(auxFileRepo.get("AMH_2019")));
        try {
            assertTrue(ageSelector.selectAuxFile(auxFileRepo.get("AMH_2019")));
        }
        catch (Exception ex) {
            System.out.println("Caught exception");;
        }
    }
    @Test
    void filterAuxFiles() {
        // L0 2020-10-02
        List<AuxFile> auxFiles = new ArrayList<>(auxFileRepo.values());
        assertDoesNotThrow(()->ageSelector.filter(auxFiles));
        try {
            List<AuxFile> filteredFiles = ageSelector.filter(auxFiles);
            assertEquals(4, filteredFiles.size());
        } catch (Exception ex) {
            System.out.println("Caught exception");;
        }
    }

}
