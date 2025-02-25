package com.csgroup.reprodatabaseline.datamodels;

import java.time.ZonedDateTime;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

public class S1ICIDTimeline {
    List<S1ICIDTimelineInterval> icidTimeline;
    public S1ICIDTimeline(List<S1ICIDTimelineInterval> timeline) {
        this.icidTimeline = timeline;
        sortTimeline();
        //checkOverlappedIntervals();
    }
    public void addInterval(S1ICIDTimelineInterval timelineInterval) {
        // TODO ; ensure that intervals are sorted, and no overlapping exists
        this.icidTimeline.add(timelineInterval);
    }
    private void sortTimeline() {
        // icidTimeline = icidTimeline.stream()
        //        .sorted(Comparator.comparing(S1ICIDTimelineInterval::getFromDate)).collect(Collectors.toList());
        Collections.sort(this.icidTimeline,
                Comparator.comparing(S1ICIDTimelineInterval::getFromDate));
    }

    public Boolean isEmpty() {
        return icidTimeline.isEmpty();
    }

    private void checkOverlappedIntervals() {
        // For each pair of consecutive intervals
        // check if first interval to date is > second interval start date
    }
    private void checkIntervalGaps() {
        // Collect any gap between consecutive intervals:
        // if first interval to date is stricly less than second interval
        // start date
    }
    private void fixGaps() {
        // For each pair of consecutive intervals
        // if first interval to date is empty or not equal to second interval start date
        // set first inteval to date to second interval start date
    }
    /**
     *
     * Retrieve the S1 ICID (Instrument Configuration ID) value
     * for the specified Satellite Unit at the given time.
     *
     * @param unit
     * @param icidTime
     * @return the icid value
     * exception: if icidTie is before first time in timeline configuration
     * or if unit is not configured
     */
    public int getIcid(ZonedDateTime icidTime) throws Exception {
        // Loop on timeline: select the interval including icidTime
        // Check: if icidTime is before first Interval
        for (S1ICIDTimelineInterval icidInterval: this.icidTimeline) {
            if (icidTime.isBefore(icidInterval.getFromDate())) {
                throw new Exception("Requested ICID for time before earliest configured value");
            }
            // Check: last interval shall not have the toDate value
            if ( icidInterval.getToDate() == null ||
                    icidTime.isBefore(icidInterval.getToDate())) {
                return icidInterval.getICID();
            }
        }
        throw new Exception("Wrong ICID Timeline configuration: last interval must be open");
    }
}
