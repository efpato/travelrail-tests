# -*- coding: utf-8 -*-

import unittest
import json
import datetime
import calendar
import urllib2
from selenium.webdriver import Firefox
from selenium.common.exceptions import NoSuchElementException

from utils import next_weekday
from controller import Controller, CabinClass, FareClass, DocumentType, TimeInterval
from passenger import Passenger


class JourneyTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(JourneyTestCase, self).__init__(*args, **kwargs)
        config = json.JSONDecoder().decode(open("config.json").read())
        self.url = config.get("url", "http://test.travelrail.ru")
        self.locale = "ru"
        self.controller = None

    def set_filter_route_options(self, count):
        response = urllib2.urlopen("{0}/admin/setfilterrouteoptions.php?value={1}/".format(self.url, count))
        self.assertEquals(200, response.code)

    def setUp(self):
        self.set_filter_route_options(1000)
        self.controller = Controller(Firefox(), self.locale)
        self.controller.driver.maximize_window()
        self.controller.driver.get(self.url)
        self.assertEqual(self.controller.driver.title, u"Путешествуй сам - TravelRail.RU", "Start page not loaded.")
        self.controller.language.click()

    def tearDown(self):
        self.controller.driver.close()
        self.set_filter_route_options(8)

    def add_passengers(self, passengers):
        for i, passenger in enumerate(passengers):
            if i > 0:
                self.controller.add_passenger.click()
            self.controller.option(self.controller.passenger_age[i], passenger.age).click()

    def set_passengers(self, passengers):
        counter = 0
        for i, passenger in enumerate(passengers):
            self.controller.first_name[i].send_keys(passenger.first_name)
            self.controller.last_name[i].send_keys(passenger.last_name)
            if passenger.is_male:
                self.controller.male[i].click()
            else:
                self.controller.female[i].click()
            if passenger.document_type is not None:
                self.controller.option(self.controller.document_type[counter], passenger.document_type).click()
            if passenger.document_number is not None:
                self.controller.document_number[counter].send_keys(passenger.document_number)
            if passenger.document_expires is not None:
                self.controller.document_expires[counter].clear()
                self.controller.document_expires[counter].send_keys(passenger.document_expires)
                counter += 1
        self.controller.email.send_keys("1234@gmail.com")
        self.controller.phone.send_keys("+79035554093")

    def set_address_info(self):
        self.controller.address.send_keys("Address")
        self.controller.city.send_keys("City")
        self.controller.state.send_keys("State")
        self.controller.zip_code.send_keys("123456")

    def agree(self):
        self.controller.general_terms_of_service.click()
        self.controller.silver_rail_terms_of_service.click()
        self.controller.custom_terms_of_service.click()

    def choose_type_of_seats(self):
        try:
            self.controller.choose_ticket_delivery_options.click()
        except NoSuchElementException:
            pass


class ATOCJourneyTestCase(JourneyTestCase):
    def test_1(self):
        origin = "Crewe"
        destination = "Stafford"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.EarlyMorning[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.AnyTimeDay,
            origin=origin,
            destination=destination,
            departure_time="06:20")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.collect_at_ticket_office.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_1CXL(self):
        self.test_1()

    def test_3(self):
        origin = "Weymouth"
        destination = "London Waterloo"
        d = next_weekday(datetime.date.today(), calendar.FRIDAY, offset=30)
        date_to = d.strftime('%d.%m.%Y')
        time_to = TimeInterval.Morning[self.locale]
        date_back = next_weekday(d, calendar.SATURDAY).strftime('%d.%m.%Y')
        time_back = TimeInterval.Morning[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys("London (All Stations)")
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.round_trip.click()
        self.controller.date_route_back.clear()
        self.controller.date_route_back.send_keys(date_back)
        self.controller.option(self.controller.time_route_back, time_back).click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.First[self.locale],
            fare_class=FareClass.AnyTimeDayReturn,
            origin=origin,
            destination=destination,
            departure_time="11:03",
            data_route_back=date_back)
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.ticket_by_dhl_international.click()
        self.set_address_info()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_3CXL(self):
        self.test_3()

    def test_7(self):
        origin = "Swansea"
        destination = "Ealing Broadway"
        date_to = next_weekday(datetime.date.today(), calendar.TUESDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.Noon[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.Advance,
            origin=origin,
            destination=destination,
            departure_time="13:28")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.ticket_by_royal_mail.click()
        self.set_address_info()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_11(self):
        origin = "Crewe"
        destination = "London Euston"
        date_to = next_weekday(datetime.date.today(), calendar.TUESDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.Afternoon[self.locale]
        passengers = [
            Passenger(
                first_name="Son1",
                last_name="Gates",
                age="10"),
            Passenger(
                first_name="Son2",
                last_name="Gates",
                age="12"),
            Passenger(
                first_name="Wife",
                last_name="Gates",
                age="23",
                is_male=False,
                document_type=DocumentType.Passport[self.locale],
                document_number="4321",
                document_expires="31.12.2030"),
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys("London (All Stations)")
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.AnyTime,
            origin=origin,
            destination=destination,
            departure_time="14:29")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.ticket_by_dhl_international.click()
        self.controller.recepient_name.send_keys("{0} {1}".format(passengers[3].first_name, passengers[3].last_name))
        self.set_address_info()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_12(self):
        origin = "Langbank"
        destination = "London Euston"
        date_to = next_weekday(datetime.date.today(), calendar.WEDNESDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.Morning[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys("London (All Stations)")
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.Advance,
            origin=origin,
            destination=destination,
            departure_time="10:29")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.collect_at_ticket_office.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_15(self):
        origin = "Manchester Piccadilly"
        destination = "London Euston"
        d = next_weekday(datetime.date.today(), calendar.THURSDAY, offset=30)
        date_to_1 = d.strftime('%d.%m.%Y')
        date_to_2 = next_weekday(d, calendar.FRIDAY).strftime('%d.%m.%Y')
        time_to_1 = TimeInterval.Noon[self.locale]
        time_to_2 = TimeInterval.Noon[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys("Manchester (All Stations)")
        self.controller.destination[0].send_keys("London (All Stations)")
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to_1)
        self.controller.option(self.controller.time[0], time_to_1).click()
        self.controller.extend_route.click()
        self.controller.origin[1].send_keys("London (All Stations)")
        self.controller.destination[1].send_keys("Manchester (All Stations)")
        self.controller.date[1].clear()
        self.controller.date[1].send_keys(date_to_2)
        self.controller.option(self.controller.time[1], time_to_2).click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.Advance,
            origin=origin,
            destination=destination,
            departure_time="12:15")
        self.assertTrue(result, "Not found result TO.")
        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.Advance,
            origin=destination,
            destination=origin,
            departure_time="12:20")
        self.assertTrue(result, "Not found result BACK.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.collect_at_ticket_office.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_17(self):
        origin = "Northampton"
        destination = "London Any Zone 1256 Station"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.EarlyMorning[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.AnyTimeDay,
            origin=origin,
            destination=destination,
            departure_time="06:18")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.collect_at_ticket_office.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_17R(self):
        origin = "London Any Zone 1256 Station"
        destination = "Northampton"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.Morning[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.AnyTimeDay,
            origin=origin,
            destination=destination,
            departure_time="09:45")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.collect_at_ticket_office.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_97(self):
        origin = "Manchester Victoria"
        destination = "Reading"
        date_to = next_weekday(datetime.date.today(), calendar.WEDNESDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.Morning[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys("Reading (All Stations)")
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.OffPeakDay,
            origin=origin,
            destination=destination,
            departure_time="09:40")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.ticket_by_royal_mail.click()
        self.set_address_info()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_98(self):
        origin = "Marks Tey"
        destination = "Heathrow Terminals 1, 2 and 3"
        date_to = next_weekday(datetime.date.today(), calendar.THURSDAY, offset=30).strftime('%d.%m.%Y')
        time_to = TimeInterval.Morning[self.locale]
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030"),
            Passenger(
                first_name="Son3",
                last_name="Gates",
                age="5")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.option(self.controller.time[0], time_to).click()
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Standard[self.locale],
            fare_class=FareClass.AnyTimeDay,
            origin=origin,
            destination=destination,
            departure_time="09:18")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.ticket_by_royal_mail.click()
        self.controller.recepient_name.send_keys("{0} {1}".format(passengers[0].first_name, passengers[0].last_name))
        self.set_address_info()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()


class RenfeJourneyTestCase(JourneyTestCase):
    def test_01(self):
        origin = "MADRID-PUERTA DE ATOCHA"
        destination = "BARCELONA-SANTS"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Club[self.locale],
            fare_class=FareClass.Flexible,
            origin=origin,
            destination=destination,
            departure_time="")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.print_at_home.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_02(self):
        origin = "MADRID-PUERTA DE ATOCHA"
        destination = "SEVILLA SANTA JUSTA"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        date_back = next_weekday(datetime.date.today(), calendar.TUESDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030"),
            Passenger(
                first_name="Son3",
                last_name="Gates",
                age="5")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.round_trip.click()
        self.controller.date_route_back.clear()
        self.controller.date_route_back.send_keys(date_back)
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Turista[self.locale],
            fare_class=FareClass.IdaYVuelta,
            origin=origin,
            destination=destination,
            departure_time="",
            data_route_back=date_back)
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.print_at_home.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_03(self):
        origin = "MADRID-PUERTA DE ATOCHA"
        destination = "ZARAGOZA-DELICIAS"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Preferente[self.locale],
            fare_class=FareClass.PromoPlus,
            origin=origin,
            destination=destination,
            departure_time="")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.print_at_home.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_04(self):
        origin = "SEVILLA SANTA JUSTA"
        destination = "MADRID-PUERTA DE ATOCHA"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        date_back = next_weekday(datetime.date.today(), calendar.TUESDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.round_trip.click()
        self.controller.date_route_back.clear()
        self.controller.date_route_back.send_keys(date_back)
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Preferente[self.locale],
            # fare_class=FareClass.Empresas,
            origin=origin,
            destination=destination,
            departure_time="",
            data_route_back=date_back)
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.print_at_home.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_05(self):
        origin = "MADRID-PUERTA DE ATOCHA"
        destination = "SEVILLA SANTA JUSTA"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030"),
            Passenger(
                first_name="Wife",
                last_name="Gates",
                age="25-54",
                is_male=False,
                document_type=DocumentType.Passport[self.locale],
                document_number="4321",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.TuristaPlus[self.locale],
            fare_class=FareClass.Promo,
            origin=origin,
            destination=destination,
            departure_time="")
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.print_at_home.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    def test_06(self):
        origin = "SEVILLA SANTA JUSTA"
        destination = "CADIZ"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        date_back = next_weekday(datetime.date.today(), calendar.TUESDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Son1",
                last_name="Gates",
                age="10"),
            Passenger(
                first_name="Son2",
                last_name="Gates",
                age="12"),
            Passenger(
                first_name="Wife",
                last_name="Gates",
                age="25-54",
                is_male=False,
                document_type=DocumentType.Passport[self.locale],
                document_number="4321",
                document_expires="31.12.2030"),
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="25-54",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.round_trip.click()
        self.controller.date_route_back.clear()
        self.controller.date_route_back.send_keys(date_back)
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        result = self.controller.find_result(
            cabin_class=CabinClass.Turista[self.locale],
            fare_class=FareClass.Flexible,
            origin=origin,
            destination=destination,
            departure_time="",
            data_route_back=date_back)
        self.assertTrue(result, "Not found result.")
        self.controller.choose_leg_solution.click()

        self.set_passengers(passengers)
        self.controller.choose_ticket_delivery_options.click()

        self.choose_type_of_seats()

        self.controller.print_at_home.click()
        self.agree()
        self.controller.proceed_to_payment.click()

        self.controller.make_payment.click()

    # ERROR: FareClass 'Tarjeta Dorada' not found.
    def test_07(self):
        origin = "MALAGA"
        destination = "MADRID-PUERTA DE ATOCHA"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="64",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.one_way.click()
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        # result = self.controller.find_result(
        #     cabin_class=CabinClass.Preferente[self.locale],
        #     fare_class=FareClass.Promo,
        #     origin=origin,
        #     destination=destination,
        #     departure_time="")
        # self.assertTrue(result, "Not found result.")
        # self.controller.choose_leg_solution.click()
        #
        # self.set_passengers(passengers)
        # self.controller.choose_ticket_delivery_options.click()
        #
        # self.choose_type_of_seats()
        #
        # self.controller.print_at_home.click()
        # self.agree()
        # self.controller.proceed_to_payment.click()
        #
        # self.controller.make_payment.click()

    # ERROR: FareClass 'Tarjeta Joven' not found.
    def test_08(self):
        origin = "BARCELONA-SANTS"
        destination = "VALENCIA JOAQUIN SOROLLA"
        date_to = next_weekday(datetime.date.today(), calendar.MONDAY, offset=30).strftime('%d.%m.%Y')
        date_back = next_weekday(datetime.date.today(), calendar.TUESDAY, offset=30).strftime('%d.%m.%Y')
        passengers = [
            Passenger(
                first_name="Bill",
                last_name="Gates",
                age="18",
                document_type=DocumentType.Passport[self.locale],
                document_number="1234",
                document_expires="31.12.2030")
        ]

        self.controller.origin[0].send_keys(origin)
        self.controller.destination[0].send_keys(destination)
        self.controller.date[0].clear()
        self.controller.date[0].send_keys(date_to)
        self.controller.round_trip.click()
        self.controller.date_route_back.clear()
        self.controller.date_route_back.send_keys(date_back)
        self.add_passengers(passengers)
        self.controller.submit_route.click()

        # result = self.controller.find_result(
        #     cabin_class=CabinClass.Turista[self.locale],
        #     fare_class=FareClass.Flexible,
        #     origin=origin,
        #     destination=destination,
        #     departure_time="",
        #     data_route_back=date_back)
        # self.assertTrue(result, "Not found result.")
        # self.controller.choose_leg_solution.click()
        #
        # self.set_passengers(passengers)
        # self.controller.choose_ticket_delivery_options.click()
        #
        # self.choose_type_of_seats()
        #
        # self.controller.print_at_home.click()
        # self.agree()
        # self.controller.proceed_to_payment.click()
        #
        # self.controller.make_payment.click()


if __name__ == "__main__":
    unittest.main(verbosity=2)
