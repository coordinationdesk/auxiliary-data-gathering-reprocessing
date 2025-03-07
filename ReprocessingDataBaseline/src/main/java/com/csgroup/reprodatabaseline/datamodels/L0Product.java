package com.csgroup.reprodatabaseline.datamodels;

/*
import org.apache.olingo.commons.api.http.HttpStatusCode;
import org.apache.olingo.server.api.ODataApplicationException;
import org.apache.olingo.server.api.ODataRequest;
import org.apache.olingo.server.api.uri.UriInfo;
import org.apache.olingo.server.api.uri.UriResource;
import org.apache.olingo.server.api.uri.UriResourceEntitySet;
import org.hibernate.annotations.Fetch;
import org.hibernate.annotations.FetchMode;
*/
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//import ch.qos.logback.core.joran.conditional.ElseAction;

import java.time.*;
import java.time.format.DateTimeFormatter;
/*
import java.sql.Timestamp;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
*/

import javax.persistence.ElementCollection;
import javax.persistence.Embedded;
import javax.persistence.Entity;
import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.EntityTransaction;
import javax.persistence.FetchType;
import javax.persistence.Id;
import javax.persistence.NoResultException;
import javax.persistence.Query;
import javax.persistence.Transient;


/**
 * @author Naceur MESKINI
 */
@Entity(name = "l0_products")
public class L0Product {
	private static final Logger LOG = LoggerFactory.getLogger(L0Product.class);

    public static class T0T1DateTime {
        public ZonedDateTime _t0;
        public ZonedDateTime _t1;
    }

    @Id
    private String name;
    private LocalDateTime validityStart;
    private LocalDateTime validityStop;

    public String getName() {
        return name;
    }

    public LocalDateTime getValidityStart() {
        return validityStart;
    }
    public LocalDateTime getValidityStop() {
        return validityStop;
    }
    public void setName(String name) {
        this.name = name;
    }

    public void setValidityStart(LocalDateTime validityStart) {
        this.validityStart = validityStart;
    }
    public void setValidityStop(LocalDateTime validityStop) {
        this.validityStop = validityStop;
    }
    public T0T1DateTime getLevel0StartStop(String platformShortName) {
        T0T1DateTime t0t1;
        if( platformShortName.equals("S3"))
        {
            t0t1 = getT0T1ForS3();

        }else if( platformShortName.equals("S2"))
        {
            t0t1 = getT0T1ForS2();

        }else
        {
            t0t1 = getT0T1ForS1();

        }
        return t0t1;
    }
    private T0T1DateTime getT0T1FromName(String prodName, int startPos, int endPos, int timeFieldLen) {
        T0T1DateTime t0t1 = new T0T1DateTime();
        t0t1._t0 = ZonedDateTime.parse(prodName.subSequence(startPos, startPos+timeFieldLen), DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
        t0t1._t1 = ZonedDateTime.parse(prodName.subSequence(endPos, endPos+timeFieldLen),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));

        return t0t1;
    }

    private T0T1DateTime getT0T1ForS3() {

        // We should read t0 and t1 from the validityStart and validityStop of the L0Product, but having the L0Product object is new and not
        // necessary for the following operation. To keep the current service stable, we left it the way it was since the launching of the service.

        // S3B_OL_0_EFR____20210418T201042_20210418T201242_20210418T215110_0119_051_242______LN1_O_NR_002.SEN3
        return getT0T1FromName(this.getName(), 16, 32, 15);
    }

    // TODO: these functions are not linked to class

    private T0T1DateTime getT0T1ForS2() {

        L0Product.T0T1DateTime t0t1 = new L0Product.T0T1DateTime();

        if ( this.getValidityStart() != null) {
            // L0Product was found on database

            // Retrieve the t0t1 from the database content
            t0t1._t0 = this.getValidityStart().atZone(ZoneId.of("UTC"));
            t0t1._t1 = this.getValidityStop().atZone(ZoneId.of("UTC"));

        } else {
            // L0Product not found

            // We read the t0t1 from the validity date contained in the file name

            // S2A_OPER_MSI_L0__LT_MTI__20150725T193419_S20150725T181440_N01.01
            t0t1._t0 = ZonedDateTime.parse(this.getName().subSequence(42, 42+15),DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss").withZone(ZoneId.of("UTC")));
            t0t1._t1 = t0t1._t0;
        }

        return t0t1;
    }

    private T0T1DateTime getT0T1ForS1() {

        // We should read t0 and t1 from the validityStart and validityStop of the L0Product, but having the L0Product object is new and not
        // necessary for the following operation. To keep the current service stable, we left it the way it was since the launching of the service.

        // S1A_IW_RAW__0SDV_20201102T203348_20201102T203421_035074_0417B3_02B4.SAFE.zip
        return getT0T1FromName(this.getName(), 17, 33, 15);
    }


}
