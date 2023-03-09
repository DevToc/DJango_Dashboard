# these are the functions that have to be run periodically
from project.bulkProcessing import bulkErrorUpdateEntrypoint


# Import from Dragon
# Import from Denodo / Product Master Data
# Import from Denodo / VRFC
# daily mail to BPS with VRFC / Projects deltas
# daily backups

# set all projects that have not been reviewed in 6 months to reviewed = false
projectReviewed

# Daily update of error table
bulkErrorUpdateEntrypoint(request)