package com.csgroup.auxip.metrics;

import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.EntityTransaction;
import javax.persistence.Query;

import org.hibernate.QueryException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.csgroup.auxip.config.MetricsConfiguration;
import com.csgroup.auxip.model.jpa.Metric;
import com.csgroup.auxip.model.jpa.MetricType;
import com.csgroup.auxip.model.jpa.Product;
import com.csgroup.auxip.model.jpa.ProductTypedCounter;
import com.csgroup.auxip.model.jpa.User;
import com.csgroup.auxip.model.repository.StorageStatus;


@Component
public class MetricsCreator {
	private static final Logger LOG = LoggerFactory.getLogger(MetricsCreator.class);
	
	@Autowired
	private StorageStatus storageStatus;
	@Autowired
	private MetricsConfiguration config;

	private static Map<String, String> SATS = new HashMap<String, String>() {{
		put("S1_", "Sentinel1.All");
		put("S1A", "Sentinel1.A");
		put("S1B", "Sentinel1.B");
		put("S2_", "Sentinel2.All");
		put("S2B", "Sentinel2.B");
		put("S2A", "Sentinel2.A");
		put("S3_", "Sentinel3.All");
		put("S3A", "Sentinel3.A");
		put("S3B", "Sentinel3.B");
	}};
	
	
	private static Map<String, List<List<String>>> SATS_FILE_TYPES = new HashMap<String, List<List<String>>>() {{
		put("S1_", new ArrayList<>(List.of(AuxTypes.S1_AUX_TYPES)));
		put("S1A", new ArrayList<>(List.of(AuxTypes.S1_AUX_TYPES)));
		put("S1B", new ArrayList<>(List.of(AuxTypes.S1_AUX_TYPES)));
		put("S2_", new ArrayList<>(List.of(AuxTypes.S2_AUX_TYPES)));
		put("S2B", new ArrayList<>(List.of(AuxTypes.S2_AUX_TYPES)));
		put("S2A", new ArrayList<>(List.of(AuxTypes.S2_AUX_TYPES)));
		put("S3_", new ArrayList<>(List.of(AuxTypes.S3_MWR_AUX_TYPES,AuxTypes.S3_OLCI_AUX_TYPES,AuxTypes.S3_SLSTR_AUX_TYPES,AuxTypes.S3_SRAL_AUX_TYPES,AuxTypes.S3_SYN_AUX_TYPES)));
		put("S3A", new ArrayList<>(List.of(AuxTypes.S3_MWR_AUX_TYPES,AuxTypes.S3_OLCI_AUX_TYPES,AuxTypes.S3_SLSTR_AUX_TYPES,AuxTypes.S3_SRAL_AUX_TYPES,AuxTypes.S3_SYN_AUX_TYPES)));
		put("S3B", new ArrayList<>(List.of(AuxTypes.S3_MWR_AUX_TYPES,AuxTypes.S3_OLCI_AUX_TYPES,AuxTypes.S3_SLSTR_AUX_TYPES,AuxTypes.S3_SRAL_AUX_TYPES,AuxTypes.S3_SYN_AUX_TYPES)));
	}};

	@Autowired
	private EntityManagerFactory entityManagerFactory;

	private static final SimpleDateFormat dateFormat = new SimpleDateFormat("HH:mm:ss");

	@Scheduled(fixedRate = 3600000, initialDelay = 5000)
	public void doMetrics() {
		if (!config.getActive())
		{
			LOG.info("Metrics are not activated in config");
			return;
		}
		LOG.info("The time is now {}", dateFormat.format(new Date()));	
		if (config.getOnTrigger() && !storageStatus.hasChanges())
		{
			LOG.info("No change in the repository, nothing to do");
			return;
		}

		//get current date
		LocalDateTime now = LocalDateTime.now();
		DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");
		//Query
		String queryString = "SELECT entity FROM com.csgroup.auxip.model.jpa.Product entity WHERE " ;
		queryString = queryString.concat("entity.Name LIKE :sat");

		for (Map.Entry<String, String> entry : SATS.entrySet()) {
			LOG.debug("Treating: "+entry.getKey());
			EntityManager entityManager = this.entityManagerFactory.createEntityManager();
			LOG.debug("Creating general Connection  ");
			try {			
				EntityTransaction transaction = entityManager.getTransaction();
				Map<String, Object> queryParams_m = new HashMap<String,Object>();						
				queryParams_m.put("sat", entry.getKey()+"%");    
				List<Product> products_m;
				Query query_m = entityManager.createQuery(queryString);
				for (Map.Entry<String, Object> entry_m : queryParams_m.entrySet()) {
					query_m.setParameter(entry_m.getKey(), entry_m.getValue());
				}
				products_m = query_m.getResultList();
				LOG.debug("Number of products : "+String.valueOf(products_m.size()));
				List<Metric> list = doMetricProducts(products_m, entry.getValue());
				
				//Product TYpe metrics
				for (List<String> types :  SATS_FILE_TYPES.get(entry.getKey()))
				{
					Map<String,Long> counts = null;
					Map<String,Long> sizes = null;
					counts = new HashMap<String,Long>();
					sizes = new HashMap<String,Long>();
					countProducts(products_m,types,counts, sizes);
					for (String type : types) {
						List<Metric> list_t = doMetricCountSize(counts.get(type), sizes.get(type), type+"."+entry.getValue());
						list.addAll(list_t);	
					}					
				}
				//Put metric in base
				transaction.begin();
				for (Metric m : list)
				{									
					Metric attached = entityManager.merge(m);
				}
				if (transaction.isActive()) {
					transaction.commit();
				} else {
					transaction.rollback();
				}				
			} finally {                    
				LOG.debug("Closing general Connection  ");
				entityManager.close();
			}
		}
		
		//User downloads metrics
		//Query
		String queryStringUser = "SELECT entity FROM com.csgroup.auxip.model.jpa.User entity" ;
		EntityManager entityManagerUser = this.entityManagerFactory.createEntityManager();
		LOG.debug("Creating User Connection  ");
		List<Metric> listMetricsUsers = new ArrayList<Metric>(); 
		try {			
			EntityTransaction transaction = entityManagerUser.getTransaction();
			List<User> users;
			Query query_m = entityManagerUser.createQuery(queryStringUser);
			users = query_m.getResultList();
			LOG.debug("Number of users : "+String.valueOf(users.size()));
			for (User u : users)
			{
				for (ProductTypedCounter count : u.getDownloadedVolumes())
				{
					//Count metric
					Metric metric = new Metric();
					metric.setName("Download."+count.getProductType()+"."+count.getPlateForm()+"."+count.getUnit()+"."+u.getName()+".size");
					metric.setMetricType(MetricType.Counter);
					metric.setCounter(count.getValue());
					metric.setGauge("");
					metric.setTimestamp(Timestamp.valueOf(LocalDateTime.now()));
					listMetricsUsers.add(metric);
				}
				for (ProductTypedCounter count : u.getNumberOfCompletedDownloads())
				{
					//Count metric
					Metric metric = new Metric();
					metric.setName("Download."+count.getProductType()+"."+count.getPlateForm()+"."+count.getUnit()+"."+u.getName()+".completed");
					metric.setMetricType(MetricType.Counter);
					metric.setCounter(count.getValue());
					metric.setGauge("");
					metric.setTimestamp(Timestamp.valueOf(LocalDateTime.now()));
					listMetricsUsers.add(metric);
				}
				for (ProductTypedCounter count : u.getNumberOfFailedDownloads())
				{
					//Count metric
					Metric metric = new Metric();
					metric.setName("Download."+count.getProductType()+"."+count.getPlateForm()+"."+count.getUnit()+"."+u.getName()+".failed");
					metric.setMetricType(MetricType.Counter);
					metric.setCounter(count.getValue());
					metric.setGauge("");
					metric.setTimestamp(Timestamp.valueOf(LocalDateTime.now()));
					listMetricsUsers.add(metric);
				}
			}
			//Put metric in base
			transaction.begin();
			for (Metric m : listMetricsUsers)
			{									
				Metric attached = entityManagerUser.merge(m);
			}
			if (transaction.isActive()) {
				transaction.commit();
			} else {
				transaction.rollback();
			}
		} catch (Exception e) {
			LOG.warn("Query coudn't be executed on metrics : "+queryStringUser);
			LOG.warn(e.getLocalizedMessage());
		} finally {                    
		        LOG.debug("Closing User Connection  ");
			entityManagerUser.close();
		}
		
		storageStatus.metricsDone();
		LOG.info("Metrics Done");

	}

	private void countProducts(final List<Product> products_m,final List<String> types,Map<String,Long> counts, Map<String,Long> sizes) {
		
		for (final String type : types)
		{
			counts.put(type, 0L);
			sizes.put(type, 0L);
		}
		for (final Product pr : products_m)
		{
			for (final String type : types)
			{
				if (pr.getName().contains(type))
				{
					counts.put(type, counts.get(type)+1L);
					sizes.put(type, sizes.get(type)+pr.getContentLength());
				}
			}
		}		
	}

	private List<Product> filterProducts(final List<Product> inProducts, final String type){
		List<Product> products = new ArrayList<>();
		for (Product pr : inProducts)
		{
			if (pr.getName().contains(type))
			{
				products.add(pr);
			}
		}
		return products;

	}

	private List<Metric> doMetricProducts(final List<Product> inProducts,final String name) {
		List<Metric> list = new ArrayList<Metric>();
		if (inProducts.size() == 0) {
			return list;
		}
		//Count metric
		Metric metric = new Metric();
		metric.setName(name+".count");
		metric.setMetricType(MetricType.Counter);
		metric.setCounter(inProducts.size());
		metric.setGauge("");
		metric.setTimestamp(Timestamp.valueOf(LocalDateTime.now()));
		list.add(metric);
		//Size metric
		long total_size =0;
		for (final Product p : inProducts)
		{
			total_size = total_size + p.getContentLength();
		}
		Metric metric_size = new Metric();
		metric_size.setName(name+".size");
		metric_size.setMetricType(MetricType.Counter);
		metric_size.setCounter(total_size);
		metric_size.setGauge("");
		metric_size.setTimestamp(Timestamp.valueOf(LocalDateTime.now()));
		list.add(metric_size);
		return list;

	}
	
	private List<Metric> doMetricCountSize(final Long count, final Long size,final String name) {
		List<Metric> list = new ArrayList<Metric>();
		if (count == 0) {
			return list;
		}
		//Count metric
		Metric metric = new Metric();
		metric.setName(name+".count");
		metric.setMetricType(MetricType.Counter);
		metric.setCounter(count);
		metric.setGauge("");
		metric.setTimestamp(Timestamp.valueOf(LocalDateTime.now()));
		list.add(metric);
		//Size metric
		Metric metric_size = new Metric();
		metric_size.setName(name+".size");
		metric_size.setMetricType(MetricType.Counter);
		metric_size.setCounter(size);
		metric_size.setGauge("");
		metric_size.setTimestamp(Timestamp.valueOf(LocalDateTime.now()));
		list.add(metric_size);
		return list;

	}


}
