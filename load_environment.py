

class ConfigLoader:
    def __init__(self, environment):
        self.environment = environment
        self.config = self.load_config()

    def load_config(self):
        if self.environment == 'dev':
            db_config = {
                'server': 'DBDEV',
                'database': 'JDE_CRP',
                'schema_main': 'CRPDTA',
                'schema_udc': 'CRPCTL'
            }
        elif self.environment == 'prod':
            db_config = {
                'server': 'ENTERPRISE',
                'database': 'JDE_PRODUCTION',
                'schema_main': 'PRODDTA',
                'schema_udc': 'PRODCTL'
            }
        else:
            raise ValueError(f"Ambiente desconhecido '{self.environment}'")
        return db_config

    def get_database_config(self):
        return self.config
