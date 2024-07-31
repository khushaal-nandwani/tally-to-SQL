class Query:
    def __init__(self, tableName):
        self.tableName = tableName
        self.fields = []
        self.values = []

    def field_exists(self, field):
        return field in self.fields

    def append_to_field(self, field, value):
        if self._do_not_add(value):
            return

        field = self._replace_single_quote(field)
        value = self._replace_single_quote(value)

        index = self.fields.index(field)
        self.values[index] = self.values[index] + value

    def add_field(self, field, value):
        if self._do_not_add(value):
            return
        
        if value.endswith(".LIST"):
            value = value[:-5] + "LIST"
        
        field = self._replace_single_quote(field)
        value = self._replace_single_quote(value)

        self.fields.append(field)
        self.values.append(value)

    def get_query(self, type):
        if len(self.fields) == 0:
            return None

        if self.tableName.endswith(".LIST"):
            self.tableName = self.tableName[:-5] + "LIST"

        for i in range(len(self.fields)):
            if self.fields[i].endswith(".LIST"):
                self.fields[i] = self.fields[i][:-5] + "LIST"

        query = "INSERT INTO " + type + self.tableName + " ("
        query += ", ".join(self.fields)
        query += ") VALUES ("
        query += ", ".join(["'" + str(value) + "'" for value in self.values])
        query += ")"
        return query

    def _do_not_add(self, value):
        if value == None:
            return True
        if value != None:
            if (
                value.strip().replace("\n", "") == ""
                or value.strip() == "Not Applicable"
            ):
                return True

    def _replace_single_quote(self, string):
        if type(string) != str:
            return None
        return string.replace("'", "''")
