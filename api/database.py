import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import Config

# Create a database engine using the URL from our configuration.
# The engine is the central point of connection to the database.
# It manages the connection pool and dialect for the specific database being used (PostgreSQL in this case).
engine = create_engine(Config.DATABASE_URL)

# Create a configured "Session" class. This class will be used to create new database sessions.
# A session is a workspace for all the objects loaded or associated with it.
# It provides the entry point to query the database.
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Create a base class for our declarative models.
# All of our database models will inherit from this class.
Base = declarative_base()
Base.query = db_session.query_property()


class AnalysisResult(Base):
    """SQLAlchemy model for the analysis_results table.

    This model defines the structure of the `analysis_results` table in the database.
    Each instance of this class represents a row in the table and stores the cached
    results of a stock analysis.
    """

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, unique=True)
    # The arima_plot is stored as a string of HTML from Plotly.
    arima_plot = Column(Text)
    # The final sentiment score is stored as a float.
    sentiment = Column(Float)
    # The Reddit posts are stored as a string representation of a list of dictionaries.
    sentiment_posts = Column(Text)
    hybrid_plot = Column(Text)  # Store the HTML for the hybrid plot
    # The last_updated timestamp is used to determine if the cached data is fresh enough to be used.
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    """Creates the database tables if they don't already exist.

    This function uses the metadata from the Base class to create all the defined tables
    in the database. It's a good practice to run this when the application starts up.
    """
    Base.metadata.create_all(bind=engine)
