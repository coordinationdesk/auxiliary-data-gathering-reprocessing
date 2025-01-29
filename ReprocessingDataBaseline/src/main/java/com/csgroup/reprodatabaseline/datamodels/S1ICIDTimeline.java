package com.csgroup.reprodatabaseline.datamodels;

import com.fasterxml.jackson.datatype.jsr310.deser.key.ZoneIdKeyDeserializer;
import org.springframework.lang.Nullable;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import java.time.ZonedDateTime;

@Entity(name = "icid_timeline")
public class S1ICIDTimeline {
    @Id
    @GeneratedValue(strategy= GenerationType.IDENTITY)
    private int id;

    private ZonedDateTime fromDate;

    @Nullable
    private ZonedDateTime toDate;

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    private String unit;

    private int ICID;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public ZonedDateTime getFromDate() {
        return fromDate;
    }

    public void setFromDate(ZonedDateTime fromDate) {
        this.fromDate = fromDate;
    }

    @Nullable
    public ZonedDateTime getToDate() {
        return toDate;
    }

    public void setToDate(@Nullable ZonedDateTime toDate) {
        this.toDate = toDate;
    }

    public int getICID() {
        return ICID;
    }

    public void setICID(int ICID) {
        this.ICID = ICID;
    }

}
