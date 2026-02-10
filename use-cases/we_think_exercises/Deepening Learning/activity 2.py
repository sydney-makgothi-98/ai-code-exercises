from datetime import datetime

from dateutil import relativedelta
from dateutil.parser import parse


class Truck:
    #Class variables
    formatted_date_str = '%Y-%m-%d'
    max_allowable_months = 3 #i.e. We must service every 3 months
    max_allowable_mileage = 200000 #in km
    high_mileage = 190000 #in km

    #Acceptable status entries
    entries = ['active', 'inactive']

    def __init__(self, vehicle_id,make,model,year,last_service_date,mileage,status):
        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
        self.year = year
        self.last_service_date = last_service_date  # We'll convert it to an actual date using the datetime class in our Truck class methods
        self.mileage = mileage
        self.status = status

    def schedule_service(self):
        messages = []
        # Error handling for Truck status
        status = self.status.lower()
        if status not in self.entries:  # .lower() accounts for entries like ACTIVE or active or ACtive etc
            return [f'Invalid entry please enter either "{self.entries[0]}" or "{self.entries[1]}"']

        if self.mileage > self.max_allowable_mileage:
            return [
                f'{self.vehicle_id} is to overdue for service and must be taken out of active service.'
            ]
        elif self.high_mileage <= self.mileage <= self.max_allowable_mileage:
            messages.append(f'{self.vehicle_id} is almost due for service')
        else:
            messages.append(f'{self.vehicle_id} is not in need of service')

        #DATE SECTION

        user_input_date = self.last_service_date
        formatted_input_date = datetime.strptime(user_input_date, self.formatted_date_str)
        #Implementing the period at which we are not allowed to exceed without having serviced the Truck (in months)
        max_date = formatted_input_date + relativedelta.relativedelta(months = self.max_allowable_months)
        current_date = datetime.now()

        if current_date > max_date:
            messages.append(f'{self.vehicle_id} is overdue for service')
        else:
            messages.append(f'{self.vehicle_id} is still well')

        return messages


#Test Inputs for Truck Class
# t_id = 'A334-BBS'
# t_type = 'Mercedes'
# t_model = 'T-63 Hauler'
# t_year = '1963'
# prev_serv_date = '2024-12-03'
# mileage = 95000
# status = 'Active'
#
# #Implementation
# Truck_obj = Truck(t_id,t_type,t_model,t_year,prev_serv_date,mileage,status)
#
# print (Truck_obj.schedule_service())

class Maintenance:
    types = ["oil change", "alignment", "general"]
    formatted_date = "%Y-%m-%d"

    def __init__(self, vehicle_id, service_type, cost, service_date):
        self.vehicle_id = vehicle_id
        self.service_type = service_type
        self.cost = cost
        self.service_date = service_date
        self.maintenance_record = []

    @staticmethod
    def is_date(date_input, fuzzy=False):
        try:
            parse(date_input, fuzzy=fuzzy)
            return True
        except ValueError:
            return False

    def maintenance_data(self):
        # Validate date
        if not self.is_date(self.service_date):
            return "Incorrect date format. Please enter the date in YYYY-MM-DD."

        # Validate service type
        if self.service_type.lower() not in self.types:
            return f"Incorrect service type. Please enter one of {', '.join(self.types)}."

        # Add record
        service_date_formatted = datetime.strptime(self.service_date, self.formatted_date)
        self.maintenance_record.append({
            "vehicle_id": self.vehicle_id,
            "service_type": self.service_type,
            "cost": self.cost,
            "service_date": service_date_formatted,
        })
        return self.maintenance_record


#Test For Maintenance and Inheritance
# t_id = 'A334-BBS'
# t_type = 'Mercedes'
# t_model = 'T-63 Hauler'
# t_year = '1963'
# prev_serv_date = '2024-12-03'
# mileage = 95000
# status = 'Active'
#
# #Implementation
# Truck_obj = Truck(t_id,t_type,t_model,t_year,prev_serv_date,mileage,status)
#
# type_of_service = 'oil change'
# cost_service = 100000
# date_of_service = '2024-10-12'
# Maintenance_obj = Maintenance(t_id,type_of_service,cost_service, date_of_service)
# print(Maintenance_obj.maintenance_data())

class FleetManager:
    def __init__(self):
        self.trucks_dict = {}

    def add_truck(self, truck_instance):
        if truck_instance.vehicle_id in self.trucks_dict:
            print(f"Truck {truck_instance.vehicle_id} already exists.")
        else:
            self.trucks_dict[truck_instance.vehicle_id] = truck_instance
            print(f"Truck {truck_instance.vehicle_id} added.")

    def remove_truck(self, vehicle_id):
        if vehicle_id in self.trucks_dict:
            del self.trucks_dict[vehicle_id]
            print(f"Truck {vehicle_id} removed.")
        else:
            print(f"Truck {vehicle_id} not found.")


if __name__ == "__main__":
    # Usage Example
    fleet_manager = FleetManager()
    truck1 = Truck("A334-BBS", "Mercedes", "T-63 Hauler", "1963", "2024-12-03", 95000, "Active")
    truck2 = Truck("B112-XYZ", "Volvo", "FH16", "2020", "2023-11-01", 180000, "Active")

    fleet_manager.add_truck(truck1)
    fleet_manager.add_truck(truck2)
    fleet_manager.remove_truck("A334-BBS")


















