package com.csgroup.auxip.model.security;


import org.apache.olingo.server.api.ODataRequest;
import org.apache.olingo.server.api.uri.UriInfo;
import org.apache.olingo.server.api.uri.UriResource;
import org.apache.olingo.server.api.uri.UriResourceEntitySet;
import org.keycloak.TokenVerifier;
import org.keycloak.representations.AccessToken;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.MessageFormat;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import com.csgroup.auxip.config.QuotasConfiguration;
import com.csgroup.auxip.config.SecurityConfiguration;
import com.csgroup.auxip.controller.AuxipBeanUtil;
import com.csgroup.auxip.model.jpa.Globals;
import com.csgroup.auxip.model.jpa.Product;
import com.csgroup.auxip.model.jpa.RoleType;
import com.csgroup.auxip.model.jpa.Subscription;
import com.csgroup.auxip.model.jpa.SystemRole;
import com.csgroup.auxip.model.jpa.User;
import com.csgroup.auxip.odata.AuxipEntityCollectionProcessor;


/**
 * @author Naceur MESKINI
 * AccessControl aims to check roles and access control of a given User
 * Think to save the user object because AccessControl can update it.
 */
public class AccessControl {
	
	private static final Logger LOG = LoggerFactory.getLogger(AccessControl.class);
	
    private User user;

    public AccessControl(){}
    public AccessControl(User user){
        this.user = user;
    }
    public void setUser(User user) {
        this.user = user;
    }
    /**
     * Check if the user can download 
     * @return
     */
    public boolean userCanDownload(){
    	if (!AuxipBeanUtil.getBean(SecurityConfiguration.class).getNeedToken())
        {
        	LOG.info("Security has been deactivated in configuration");
        	return true;
        }

        QuotasConfiguration quotasConfiguration = AuxipBeanUtil.getBean(QuotasConfiguration.class);

        LocalDateTime periodStart = this.user.getDownloadedVolume().getPeriodStart() ;
        LocalDateTime periodEnd =  periodStart.plus(quotasConfiguration.getTotalDownloadsPeriod()) ;

        LocalDateTime parallelStart = this.user.getLastDownloadDateTime() ;
        LocalDateTime parallelEnd =  parallelStart.plus(quotasConfiguration.getParallelDownloadsDeltaTime()) ;
        
        LocalDateTime now = LocalDateTime.now() ;
        if( now.isAfter( parallelEnd ) )
        {
            // start a new parallel counting 
            this.user.setNumberOfParallelDownloads(0);
            this.user.setLastDownloadDateTime(now);
        }

        if( now.isAfter( periodEnd ) )
        {
            // start a new period and a new counting
            this.user.getDownloadedVolume().setVolume(0);
            this.user.getDownloadedVolume().setPeriodStart(now);
            return true;
        }else
        {
            List<RoleType> rolesTypes = new ArrayList<>();
            for(SystemRole role : this.user.getRoles() )
            {
                rolesTypes.add( role.getName() );
            }
            // User role should be "Download" and volume not exceeded the quota  ( first convert volume from Bytes to Giga Bytes )
            Boolean canDownload =  ( rolesTypes.contains(RoleType.download) && 
                   ( this.user.getDownloadedVolume().getVolume() * 10e-9  < quotasConfiguration.getTotalDownloadsQuota() ) &&
                   ( this.user.getNumberOfParallelDownloads()  < quotasConfiguration.getParallelDownloadsQuota() ) ) ;
            String logMessage = MessageFormat.format("The user \"{0}\" has downloaded {1} out of {2}. The number of his parallel downloads is {3} out of {4}.",
                                                this.user.getName(),
                                                this.user.getDownloadedVolume().getVolume() * 10e-9,
                                                quotasConfiguration.getTotalDownloadsQuota(),
                                                this.user.getNumberOfParallelDownloads(),
                                                quotasConfiguration.getParallelDownloadsQuota());
            if (!canDownload) {
            	// The user is not allowaed to download
            	
                LOG.error(logMessage);

            } else {
            	// The user is allowed to download
            	
                LOG.info(logMessage);
            }
                
            return canDownload;
        }
    }
    /**
     * Check if the user has ability to run this request with a given uriinfo
     * @param request : Odata request
     * @param uriInfo : Uri informations
     * @return boolean
     */
    public static boolean userCanDealWith( ODataRequest request ,  UriInfo uriInfo)
    {
        if (!AuxipBeanUtil.getBean(SecurityConfiguration.class).getNeedToken())
        {
        	LOG.info("Security has been deactivated in configuration");
        	return true;
        }
        AccessToken token;
        try
        {
            String bearerToken = request.getHeader("Authorization").replace("Bearer ", "") ;
            token = TokenVerifier.create(bearerToken,AccessToken.class).getToken();
            
        }catch (Exception e)
        {
           return false;
        } 

        Set<String> keycloakRoles = token.getRealmAccess().getRoles();

        // Get EntitySet Name
        UriResource uriResource = uriInfo.getUriResourceParts().get(0); 
        UriResourceEntitySet uriResourceEntitySet = (UriResourceEntitySet) uriResource;
        String EntitySetName = uriResourceEntitySet.getEntitySet().getName();

        // Administration Services
        // (Monitoring &) Reporting – Monitoring and Reporting functionality, including the permission to
        // perform queries on all properties.
        if ( keycloakRoles.contains(Globals.REPORTING_ROLE)  )
        {
            // yes for all entities and proporties
            return true;
        }

        // Client Services
        // Download => The client may perform queries on the products available at the AUXIP and perform downloads
        // ! may be with download role , one can create/mange subscriptions !
        if ( keycloakRoles.contains(Globals.DOWNLOAD_ROLE) && ( EntitySetName.equals(Product.ES_NAME) || EntitySetName.equals(Subscription.ES_NAME)) )
        {
            // allow access only for Products/Subscriptions entitySet
            return true;
        }

        return false;

    }

}
