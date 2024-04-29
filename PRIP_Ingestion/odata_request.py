# Utility functions to build a OData request_
def _add_odata_top(odata_request, top_num_result):
    return odata_request + "&$top="+str(top_num_result)

def _add_odata_skip(odata_request, skip_results):
    return odata_request + "&$skip="+str(skip_results)

def build_paginated_request(odata_request, start, step):
    stop = start + step
    request_top = _add_odata_top(odata_request, step)
    request_top = _add_odata_skip(request_top, start)
    return request_top

