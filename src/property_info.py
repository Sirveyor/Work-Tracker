class PropertyInfo:
    """
    A class to store information related to a property.

    Attributes:
        job_number (str): The job number associated with the property.
        property_address (str): The address of the property.
        tax_id (str): The tax ID of the property.
        county (str): The county where the property is located.
        subdivision_name (str): The name of the subdivision where the property is located.
        lot_number (str): The lot number of the property.
        block_number (str): The block number of the property.
        owner_name (str): The name of the property owner.
        owner_phone (str): The phone number of the property owner.
        owner_address (str): The address of the property owner if different from the property address.
        requester_name (str): The name of the requester if different from the owner.
        requester_phone (str): The phone number of the requester if different from the owner.
        access_restrictions (str): Any access restrictions like locked fences.
        requested_services (str): The services requested for the property.
        expected_due_date (str): The expected due date for the services.
    """

    def __init__(self, job_number, property_address, tax_id, county, subdivision_name, lot_number, block_number, owner_name, owner_phone,
                 owner_address=None, requester_name=None, requester_phone=None,
                 access_restrictions=None, requested_services=None, expected_due_date=None):
        self.job_number = job_number
        self.property_address = property_address
        self.tax_id = tax_id
        self.county = county
        self.subdivision_name = subdivision_name
        self.lot_number = lot_number
        self.block_number = block_number
        self.owner_name = owner_name
        self.owner_phone = owner_phone
        self.owner_address = owner_address
        self.requester_name = requester_name
        self.requester_phone = requester_phone
        self.access_restrictions = access_restrictions
        self.requested_services = requested_services
        self.expected_due_date = expected_due_date


def gather_property_info():
    """
    Gathers property information from the user.

    Returns:
        PropertyInfo: An instance of PropertyInfo containing the gathered data.
    """
    job_number = input("Enter job number: ")
    property_address = input("Enter property address: ")
    tax_id = input("Enter tax ID: ")
    county = input("Enter county: ")
    subdivision_name = input("Enter subdivision name: ")
    lot_number = input("Enter lot number: ")
    block_number = input("Enter block number: ")
    owner_name = input("Enter property owner's name: ")
    owner_phone = input("Enter property owner's phone number: ")
    owner_address = input("Enter owner's address (if different from property address): ")
    requester_name = input("Enter requester's name (if different from owner's name): ")
    requester_phone = input("Enter requester's phone number (if different from owner's phone number): ")
    access_restrictions = input("Enter access restrictions (e.g., locked fences): ")
    requested_services = input("Enter requested services: ")
    expected_due_date = input("Enter expected due date (YYYY-MM-DD): ")

    return PropertyInfo(job_number, property_address, tax_id, county, subdivision_name, lot_number,
                        block_number, owner_name, owner_phone, owner_address,
                        requester_name, requester_phone, access_restrictions, requested_services,
                        expected_due_date)
