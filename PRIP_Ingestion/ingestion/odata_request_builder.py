
class ODataRequestBuilder:
    def __init__(self, base_url):
        self._base_url = base_url

    def _build_get_simple_base_request(self):
        get_request = self._base_url + "/Products?$orderby=PublicationDate asc"
        return get_request

    def build_get_names_base_request(self,
                                      names_list,
                                    expand=False):
        get_request = self._build_get_simple_base_request() + \
                    "&$filter="
        get_request += "("
        get_request += f"contains(Name,'{names_list[0]}')"
        for prod_name in names_list[1:]:
            if prod_name:
                get_request += f" or contains(Name,'{prod_name}')"
        get_request += ")"
        if expand:
            get_request += "&$expand=Attributes"
        return get_request

    def build_get_base_request(self,
                               type_list, sat,
                               from_date, to_date,
                                    expand=False):
        # Check: if not type and no date was specified,
        # request cannot be build
        if not from_date and not to_date and len(type_list) == 0:
            raise Exception("Archive Request without either type or date condition cannot be issued")
        # TODO: Modify to manage from_date not specified
        get_request = self._build_get_simple_base_request() + \
                    "&$filter="
        if from_date and len(from_date):
            # TODO: make also Date field parametric
            get_request = get_request + " PublicationDate gt " + from_date
        if to_date and len(to_date):
            conjunction = " and " if from_date else " "
            # TODO: make also Date field parametric
            get_request = get_request + conjunction + " PublicationDate lt " + to_date
        if from_date or to_date:
            # And conjunction is needed if at least one time condition was specified
            get_request = get_request + " and "
        if len(type_list) > 1:
            get_request += "("
        get_request += f"contains(Name,'{type_list[0]}')"
        for prod_type in type_list[1:]:
            get_request += f" or contains(Name,'{prod_type}')"
        if len(type_list) > 1:
            get_request += ")"
        if sat:
            get_request += " and startswith(Name,'"+sat+"')"
        if expand:
            get_request += "&$expand=Attributes"
        return get_request
    
