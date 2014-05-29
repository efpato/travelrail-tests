# -*- coding: utf-8 -*-


class TimeInterval:
    EarlyMorning = {"ru": u"Раннее утро 06:00", "en": u"Early morning 06:00"}
    Morning = {"ru": u"Утро (09:00)", "en": u"Morning (09:00)"}
    Noon = {"ru": u"Полдень (12:00)", "en": u"Noon (12:00)"}
    Afternoon = {"ru": u"В обед (14:00)", "en": u"Afternoon (14:00)"}
    Evening = {"ru": u"Вечер (18:00)", "en": u"Evening (18:00)"}
    LateEvening = {"ru": u"Поздний вечер (21:00)", "en": u"Late evening (21:00)"}


class CabinClass:
    Standard = {"ru": "Стандартный класс", "en": "Standard"}
    First = {"ru": "Первый класс", "en": "first"}
    Club = {"ru": "Club", "en": "Club"}
    Turista = {"ru": "Turista", "en": "Turista"}
    TuristaPlus = {"ru": "Turista Plus", "en": "Turista Plus"}
    Preferente = {"ru": "Preferente", "en": "Preferente"}


class FareClass:
    AnyTime = "ANYTIME "
    AnyTimeDay = "ANYTIME_DAY "
    AnyTimeDayReturn = "ANYTIME_DAY_RETURN"
    OffPeakDay = "OFFPEAK_DAY"
    Advance = "ADVANCE"
    Flexible = "FLEXIBLE"
    Ninos = "NINOS"
    Promo = "PROMO "
    PromoPlus = "PROMOPLUS"
    IdaYVuelta = "IDAYVUELTA"
    Empresas = "EMPRESAS"
    Tarjeta = "TORJETA"
    Dorada = "DORADA"
    Joven = "JOVEN"


class DocumentType:
    Passport = {"ru": u"Паспорт", "en": u"Traveller passport"}


class DeliveryOption:
    CollectAtTicketOffice = {"ru": "В билетной кассе", "en": "Collect at Ticket Office"}
    TicketByDHLInternational = {"ru": "Ticket by International DHL Next Day", "en": "Ticket by International DHL Next Day"}
    TicketByRoyalMail = {"ru": "Почтовым сервисом Royal Mail", "en": "Ticket by Royal Mail"}
    PrintAtHome = {"ru": "Print At Home", "en": "Print At Home"}


class Controller:
    LOCALE = {"ru": "Русский", "en": "English"}
    ONE_WAY = {"ru": "В одну сторону", "en": "One way"}
    ROUND_TRIP = {"ru": "Туда и обратно", "en": "Round trip"}
    EXTEND_ROUTE = {"ru": "Продолжить маршрут", "en": "Extend route"}
    ADD_PASSENGER = {"ru": "Добавить пассажира", "en": "Add passenger"}
    SUBMIT_ROUTE = {"ru": "Найти билеты", "en": "Submit route"}
    CHOOSE_LEG_SOLUTION = {"ru": "К покупке билета", "en": "Choose leg solution"}
    CHOOSE_TICKET_DELIVERY_OPTIONS = {"ru": "Выбрать вариант доставки билета", "en": "Choose ticket delivery options"}
    PROCEED_TO_PAYMENT = {"ru": "Перейти к оплате", "en": "Proceed to payment"}
    MAKE_PAYMENT = {"ru": "Произвести платеж", "en": "Make payment"}

    def __init__(self, driver, locale):
        self.driver = driver
        self.locale = locale

    @staticmethod
    def option(select, text):
        for option in select.find_elements_by_tag_name("option"):
            if option.text == text:
                return option

    def find_result(self, cabin_class, fare_class, origin, destination, departure_time, data_route_back=False):
        results = dict()
        elements = self.driver.find_elements_by_xpath(
            '//a[@data-parent="#accordion-results" and contains(., "{0} {1}")]'.format(
                cabin_class, fare_class)
        )
        for result in elements:
            results[result.get_attribute("href").split("#")[1]] = result

        for key in results.keys():
            table = self.driver.find_element_by_xpath("//div[@id='{0}']/div/form/table".format(key))
            if not data_route_back:
                lines = table.find_elements_by_xpath(
                    './/tr['
                    'td[2]//text()[contains(., "{0}")] and '
                    'td[2]//text()[contains(., "{1}")] and '
                    'td[3]//text()[contains(., "{2}")]'
                    ']'.format(origin, departure_time, destination))
                if lines:
                    if not table.is_displayed():
                        results[key].click()
                    lines.pop(0).click()
                    return True
            else:
                lines = table.find_elements_by_xpath(
                    './/tr[('
                    'td[2]//text()[contains(., "{0}")] and '
                    'td[2]//text()[contains(., "{1}")] and '
                    'td[3]//text()[contains(., "{2}")]'
                    ') or ('
                    'td[2]//text()[contains(., "{2}")] and '
                    'td[3]//text()[contains(., "{0}")]'
                    ')]'.format(origin, departure_time, destination))
                if len(lines) >= 2:
                    if not table.is_displayed():
                        results[key].click()
                    lines.pop(0).click()
                    return True
        return False

    @property
    def language(self):
        return self.driver.find_element_by_link_text(self.LOCALE[self.locale])

    @property
    def submit_route(self):
        return self.driver.find_element_by_xpath(
            "//input[@type='submit' and @value='{0}']".format(self.SUBMIT_ROUTE[self.locale]))

    @property
    def extend_route(self):
        return self.driver.find_element_by_link_text(self.EXTEND_ROUTE[self.locale])

    @property
    def add_passenger(self):
        return self.driver.find_element_by_link_text(self.ADD_PASSENGER[self.locale])

    @property
    def origin(self):
        return self.driver.find_elements_by_xpath("//input[contains(@name, 'froms_')]")

    @property
    def destination(self):
        return self.driver.find_elements_by_xpath("//input[contains(@name, 'tos_')]")

    @property
    def one_way(self):
        return self.driver.find_element_by_xpath('//button[@type="button" and @data-value="1"]')

    @property
    def round_trip(self):
        return self.driver.find_element_by_xpath('//button[@type="button" and @data-value="2"]')

    @property
    def date(self):
        return self.driver.find_elements_by_xpath("//input[contains(@name, 'dates_')]")

    @property
    def date_route_back(self):
        return self.driver.find_element_by_name("dates_roundTripBack")

    @property
    def time(self):
        return self.driver.find_elements_by_xpath("//select[contains(@name, 'times_')]")

    @property
    def time_route_back(self):
        return self.driver.find_element_by_name("times_roundTripBack")

    @property
    def passenger_age(self):
        return self.driver.find_elements_by_xpath("//select[contains(@name, 'passengerAge')]")

    @property
    def choose_leg_solution(self):
        buttons = self.driver.find_elements_by_xpath(
            "//input[@type='submit' and @value='{0}']".format(self.CHOOSE_LEG_SOLUTION[self.locale]))
        for button in buttons:
            if button.is_displayed():
                return button

    @property
    def first_name(self):
        return self.driver.find_elements_by_xpath("//input[contains(@name, 'firstName_')]")

    @property
    def last_name(self):
        return self.driver.find_elements_by_xpath("//input[contains(@name, 'lastName_')]")

    @property
    def male(self):
        return self.driver.find_elements_by_xpath(
            '//input[@type="radio" and @value="m" and contains(@name, "gender_")]')

    @property
    def female(self):
        return self.driver.find_elements_by_xpath(
            '//input[@type="radio" and @value="f" and contains(@name, "gender_")]')

    @property
    def document_type(self):
        return self.driver.find_elements_by_xpath("//select[contains(@name, 'documentType_')]")

    @property
    def document_number(self):
        return self.driver.find_elements_by_xpath("//input[contains(@name, 'documentNumber_')]")

    @property
    def document_expires(self):
        return self.driver.find_elements_by_xpath("//input[contains(@name, 'documentExpiresOn_')]")

    @property
    def email(self):
        return self.driver.find_element_by_name("email")

    @property
    def phone(self):
        return self.driver.find_element_by_name("phone")

    @property
    def choose_ticket_delivery_options(self):
        return self.driver.find_element_by_xpath(
            "//input[@type='submit' and @value='{0}']".format(self.CHOOSE_TICKET_DELIVERY_OPTIONS[self.locale]))

    @property
    def collect_at_ticket_office(self):
        return self.driver.find_element_by_xpath(
            "//label[contains(text(), '{0}')]/input[@name='ticketDeliveryOption']".format(
                DeliveryOption.CollectAtTicketOffice[self.locale]))

    @property
    def ticket_by_dhl_international(self):
        return self.driver.find_element_by_xpath(
            "//label[contains(text(), '{0}')]/input[@name='ticketDeliveryOption']".format(
                DeliveryOption.TicketByDHLInternational[self.locale]))

    @property
    def ticket_by_royal_mail(self):
        return self.driver.find_element_by_xpath(
            "//label[contains(text(), '{0}')]/input[@name='ticketDeliveryOption']".format(
                DeliveryOption.TicketByRoyalMail[self.locale]))

    @property
    def print_at_home(self):
        return self.driver.find_element_by_xpath(
            "//label[contains(text(), '{0}')]/input[@name='ticketDeliveryOption']".format(
                DeliveryOption.PrintAtHome[self.locale]))

    @property
    def recepient_name(self):
        return self.driver.find_element_by_name("recepientName")

    @property
    def address(self):
        return self.driver.find_element_by_name("address")

    @property
    def city(self):
        return self.driver.find_element_by_name("city")

    @property
    def state(self):
        return self.driver.find_element_by_name("state")

    @property
    def zip_code(self):
        return self.driver.find_element_by_name("zipCode")

    @property
    def country(self):
        return self.driver.find_element_by_name("country")

    @property
    def address_type(self):
        return self.driver.find_element_by_name("addressType")

    @property
    def general_terms_of_service(self):
        return self.driver.find_element_by_xpath("//input[@type='checkbox' and @name='generalTOS']")

    @property
    def silver_rail_terms_of_service(self):
        return self.driver.find_element_by_xpath("//input[@type='checkbox' and @name='silverRailTOS']")

    @property
    def custom_terms_of_service(self):
        return self.driver.find_element_by_xpath("//input[@type='checkbox' and @name='customTOS']")

    @property
    def proceed_to_payment(self):
        return self.driver.find_element_by_xpath(
            "//input[@type='submit' and @value='{0}']".format(self.PROCEED_TO_PAYMENT[self.locale]))

    @property
    def make_payment(self):
        return self.driver.find_element_by_xpath(
            "//input[@type='submit' and @value='{0}']".format(self.MAKE_PAYMENT[self.locale]))
