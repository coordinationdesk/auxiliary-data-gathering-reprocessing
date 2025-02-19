package com.csgroup.reprodatabaseline.selectors;
import com.csgroup.reprodatabaseline.datamodels.AuxFile;
import com.csgroup.reprodatabaseline.datamodels.L0Product;
import com.csgroup.reprodatabaseline.datamodels.S1ICIDTimeline;
import com.csgroup.reprodatabaseline.datamodels.S1ICIDTimelineInterval;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class IcidTimelineTest {
    private S1ICIDTimeline icidCOnfiguration ;
    @BeforeEach
    void setUp() {
        // FIll configuration
        // Define a timeline with followin gproperties:
        // intervals are inserted out of time order
        // (interval have gaps)
        // Last interval as TO set to NULL
        // IID values are monotonic, excepted two intervals :
        // ICID 1 is present in two intervals, mixed with ICID2 value
        // ICID 5 value is present in two intervals
        List<S1ICIDTimelineInterval> intervals;
        intervals = new ArrayList<>();
        ZonedDateTime intervalStart = ZonedDateTime.parse("2014-03-01T00:00:00Z");
        ZonedDateTime intervalStop = ZonedDateTime.parse("2016-04-03T12:00:00Z");
        S1ICIDTimelineInterval icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(1);
        intervals.add(icidInterval);
        // ICID 2
        intervalStart = ZonedDateTime.parse("2016-04-03T12:00:00Z");
        intervalStop = ZonedDateTime.parse("2016-05-13T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(2);
        intervals.add(icidInterval);
        // New interval with ICID 1
        intervalStart = ZonedDateTime.parse("2016-05-13T00:00:00Z");
        intervalStop = ZonedDateTime.parse("2016-06-02T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(1);
        intervals.add(icidInterval);
        // Again ICID 2
        intervalStart = ZonedDateTime.parse("2016-06-02T00:00:00Z");
        intervalStop = ZonedDateTime.parse("2017-05-13T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(2);
        intervals.add(icidInterval);
        // ICID 3
        intervalStart = ZonedDateTime.parse("2017-05-13T00:00:00Z");
        intervalStop = ZonedDateTime.parse("2018-02-05T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(3);
        intervals.add(icidInterval);
        // ICID 4
        intervalStart = ZonedDateTime.parse("2018-02-05T00:00:00Z");
        intervalStop = ZonedDateTime.parse("2018-05-25T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(4);
        intervals.add(icidInterval);
        // ICID 5
        intervalStart = ZonedDateTime.parse("2018-05-25T00:00:00Z");
        intervalStop = ZonedDateTime.parse("2018-06-15T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(5);
        intervals.add(icidInterval);
        // Again ICID 4
        intervalStart = ZonedDateTime.parse("2018-06-15T00:00:00Z");
        intervalStop = ZonedDateTime.parse("2018-07-11T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(4);
        intervals.add(icidInterval);
        // Returnt to ICID 5
        intervalStart = ZonedDateTime.parse("2018-07-11T00:00:00Z");
        intervalStop = ZonedDateTime.parse("2020-11-11T00:00:00Z");
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(5);
        intervals.add(icidInterval);
        // ICID 6 (last value)
        intervalStart = ZonedDateTime.parse("2020-11-11T00:00:00Z");
        intervalStop = null;
        icidInterval = new S1ICIDTimelineInterval();
        icidInterval.setFromDate(intervalStart);
        icidInterval.setToDate(intervalStop);
        icidInterval.setICID(6);
        intervals.add(icidInterval);
        icidCOnfiguration = new S1ICIDTimeline(intervals);
    }
    @Test
    void whenLoadedTimeline_thenSortedIntervals() {
        // Loop on Icid Timelien
        // for each interval check that start time is before next interval start time
    }
    @Test
    void whenFirstInterval_thenFirstIcid() {
        ZonedDateTime referenceTime = ZonedDateTime.parse("2015-07-01T11:10:00Z");
        try {
            assertEquals(1, icidCOnfiguration.getIcid(referenceTime));
        } catch (Exception ex) {

        }

    }
    // TEst should check retrieving of icid values for:
    // a time breofre start of timeline
    @Test
    void whenBeforeFirstInterval_thenException() {
        ZonedDateTime referenceTime = ZonedDateTime.parse("2012-07-01T11:10:00Z");
        try {
            assertThrows(Exception.class, () -> icidCOnfiguration.getIcid(referenceTime));
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
    // a time after end of timeline
    @Test
    void whenTimeAfterLastIntervalStart_thenGetLastIcidValue() {
        ZonedDateTime referenceTime = ZonedDateTime.parse("2024-07-01T23:20:00Z");
        try {
            assertEquals(6, icidCOnfiguration.getIcid(referenceTime));
        } catch (Exception ex) {

        }

    }
    // an interval with a value present only in one single interval
    @Test
    void whenIcidSingleInterval_thenGetValue() {
        ZonedDateTime referenceTime = ZonedDateTime.parse("2017-12-01T13:20:00Z");
        try {
            assertEquals(3, icidCOnfiguration.getIcid(referenceTime));
        } catch (Exception ex) {

        }

    }
    // and interval with a value present in more than one interval
    @Test
    void whenIcidMultiple_thenGetCorrectValue() {
        ZonedDateTime referenceTime = ZonedDateTime.parse("2016-05-16T10:00:00Z");
        try {
            assertEquals(1, icidCOnfiguration.getIcid(referenceTime));
        } catch (Exception ex) {

        }
        referenceTime = ZonedDateTime.parse("2017-03-05T00:00:00Z");
        try {
            assertEquals(2, icidCOnfiguration.getIcid(referenceTime));
        } catch (Exception ex) {

        }
    }
}
