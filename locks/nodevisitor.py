class NodeVisitor:
    def visit(self, node):
        fn_name = f'visit_{type(node).__name__}'
        fn = getattr(self, fn_name, self.no_visit_method)
        return fn(node)

    def no_visit_method(self, node):
        raise Exception(f'no visit_{type(node).__name__} method found')