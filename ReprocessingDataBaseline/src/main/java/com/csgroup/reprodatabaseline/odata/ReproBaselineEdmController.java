package com.csgroup.reprodatabaseline.odata;

import java.io.IOException;
import java.util.ArrayList;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletRequestWrapper;
import javax.servlet.http.HttpServletResponse;

import javax.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.apache.olingo.server.api.OData;
import org.apache.olingo.server.api.ODataHttpHandler;
import org.apache.olingo.server.api.ServiceMetadata;
import org.apache.olingo.commons.api.edmx.EdmxReference;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * The Class ReproBaselineEdmController.
 *
 * @author Naceur MESKINI
 */
@RestController
@RequestMapping(ReproBaselineEdmController.URI)
public class ReproBaselineEdmController {

    private static final Logger LOG = LoggerFactory.getLogger(ReproBaselineEdmController.class);
	public static final String URI = "/rdb.svc";
    @Autowired
    private ReproDataBaseline  reproBaseline;
    OData odata;
    ServiceMetadata edm;
    
    @PostConstruct
    public void postConstruct() {
    	odata = OData.newInstance();
        edm = odata.createServiceMetadata(new ReproBaselineEdmProvider(), new ArrayList<EdmxReference>());
    }
	/**
	 * Process.
	 *
	 * @param request the req
	 * @param response the Http response
	 * @throws IOException
	 */
	@RequestMapping("**")
	public void process(HttpServletRequest request, HttpServletResponse response){
        try {

            // create odata handler and configure it with EdmProvider and Processor
            //ServiceMetadata edm = odata.createServiceMetadata(new AuxipEdmProvider(), new ArrayList<EdmxReference>());
            ODataHttpHandler handler = odata.createHandler(edm);
            // TODO Replace with ReproDataBaseline (autowired)
            handler.register(new ReproBaselineEntityCollectionProcessor(reproBaseline));
            
            // let the handler do the work
            handler.process(new HttpServletRequestWrapper(request) {
                // Spring MVC matches the whole path as the servlet path
                // Olingo wants just the prefix, ie upto /auxipv2, so that it
                // can parse the rest of it as an OData path. So we need to override
                // getServletPath()
                @Override
                public String getServletPath() {
                    return ReproBaselineEdmController.URI;
                }
                // Override getRequestURL to resolve the '/' problem
                // the problem occurs while filling Odata Uri informations  (in Odata function => fillUriInformation)
                @Override
                public StringBuffer getRequestURL() {
                    if(request.getRequestURI().equals(ReproBaselineEdmController.URI))
                        return request.getRequestURL().append("/"); 
                    else
                    {
                        return request.getRequestURL();
                    }
                }

            }, response);
          } catch (RuntimeException e) {
            LOG.error("Server Error occurred in Auxip service", e);
          }
        }
}
