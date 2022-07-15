from flask import request
from marshmallow import Schema, fields
from urllib.parse import urlencode


class PaginationSchema(Schema):
    
    class Meta:
        ordered = True
    
    # Specify how to serialize the pages
    links = fields.Method(serialize='get_pagination_links')
    # The current page
    page = fields.Integer(dump_only=True)
    # The total number of pages
    pages = fields.Integer(dump_only=True)
    # The number of records per page
    per_page = fields.Integer(dump_only=True)
    # The total of records
    totals = fields.Integer(dump_only=True)
    
    # Generate the URL of the page based on the page number
    # http://127.0.0.1:5000/recipes?per_page=2&page=1
    @staticmethod
    def get_url(page):
        query_args = request.args.to_dict()
        query_args['page'] = page
        return f'{request.base_url}?{urlencode(query_args)}'
    
    # Base on the Paginated Object, set 'first', 'last', 'prev', 'next' for attribute links to generate the URL
    def get_pagination_links(self, paginated_obj):
        pagination_links = {
            'first': self.get_url(page=1),
            'last': self.get_url(page=paginated_obj.pages)
        }
        if paginated_obj.has_prev:
            pagination_links['prev'] = self.get_url(page=paginated_obj.prev_num)
        if paginated_obj.has_next:
            pagination_links['next'] = self.get_url(page=paginated_obj.next_num)
        return pagination_links
    