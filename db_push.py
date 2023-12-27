import utils.database

Base = utils.database.Database().Base

Base.metadata.drop_all(utils.database.Database().engine)
Base.metadata.create_all(utils.database.Database().engine)
