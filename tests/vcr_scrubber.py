import json
import re
import uuid
from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from faker import Faker

FAKE_USER_ID = "7c9bbfae-0000-47b7-0000-0e66d868c2cf"
FAKE_TIMESTAMP_MS = 1574303699770
FAKE_ISO_TIMESTAMP = "2020-01-01T00:00:00.000Z"

ADDRESS_FIELDS = frozenset(
    {
        "city",
        "country",
        "line1",
        "line2",
        "postalCode",
        "postcode",
        "state",
        "street",
        "suburb",
        "zip",
    }
)

SENSITIVE_QUERY_PARAMS = frozenset({"reference"})

PRESERVE_ID_FIELDS = frozenset(
    {
        "currencyID",
        "finTranTypeID",
        "instrumentTypeID",
    }
)

UUID_IN_PATH_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _scrub_context():
    fake = Faker()
    fake.seed_instance(1234)
    fake_order_id = uuid.UUID(str(uuid.uuid3(uuid.NAMESPACE_URL, "test")), version=4)
    fake_transaction_id = f"HHI.{fake_order_id}"
    fake_reference = fake.pystr_format()
    fake_account_code = fake.pystr_format()

    obfuscated_fields = {
        "accountAmount": 1.0,
        "accountBalance": 1000.0,
        "accountNumber": fake_account_code,
        "ackSignedWhen": str(fake.date_this_decade()),
        "brokerInstructionId": str(fake_order_id),
        "brokerInstructionVersionId": str(fake_order_id),
        "brokerOrderId": 11111,
        "brokerOrderVersionId": str(fake_order_id),
        "bsb": fake.pystr_format(),
        "buyOrderNumber": fake_account_code,
        "buyingPower": 1000.0,
        "cardHoldAmount": 0.0,
        "cashAvailableForExpressWithdrawal": 1000,
        "cashAvailableForTrade": 800,
        "cashAvailableForWithdrawal": 1000,
        "cashAvailableForWithdrawalHold": 0.0,
        "cashAvailableForWithdrawalRaw": 1000,
        "cashAvailableForTransfer": 1000,
        "cashBalance": 1000.0,
        "clearingCash": 0.0,
        "comment": fake.pystr_format(),
        "contractNoteNumber": 11111,
        "contractNoteNumbers": [11111],
        "cpfValue": None,
        "createdDate": FAKE_TIMESTAMP_MS,
        "createdWhen": str(fake.date_time_this_decade()),
        "cumQty": "0",
        "dateOfBirth": None,
        "dw_AccountId": str(fake_order_id),
        "dw_AccountNumber": fake_account_code,
        "dw_id": str(fake_order_id),
        "dwAccountId": str(fake_order_id),
        "dwCashAvailableForWithdrawal": 1000,
        "dwOrderId": fake_transaction_id,
        "emailAddress": fake.email(),
        "finTranID": str(fake_order_id),
        "firstName": fake.first_name(),
        "fromAmount": 1000.0,
        "fundsInFlight": 0.0,
        "insertDate": FAKE_TIMESTAMP_MS,
        "instrumentCodeId": str(fake_order_id),
        "instrumentId": str(fake_order_id),
        "instrumentID": str(fake_order_id),
        "itemId": str(fake_order_id),
        "lastName": fake.last_name(),
        "ledgerBalance": 0.0,
        "liquidCash": 1000.0,
        "macAccountNumber": fake_account_code,
        "masterAccountId": None,
        "middleName": None,
        "newWatchlistId": str(fake_order_id),
        "openQty": 100,
        "orderID": fake_transaction_id,
        "orderId": fake_transaction_id,
        "orderNo": fake_account_code,
        "password": fake.password(),
        "pendingOrdersAmount": 0.0,
        "pendingPoliAmount": 0.0,
        "pendingWithdrawals": 0.0,
        "phoneNumber": fake.phone_number(),
        "postedBalance": 4000,
        "productWatchlistID": str(fake_order_id),
        "realizedPL": 1.0,
        "reference": fake_reference,
        "referenceNumber": fake_account_code,
        "referralCode": fake_account_code,
        "referredByCode": None,
        "reservedCash": 0.0,
        "rewardJourneyTimestamp": None,
        "sellOrderNumber": fake_account_code,
        "settledCash": 10000.00,
        "stakeApprovedDate": None,
        "stakeInstrumentId": str(fake_order_id),
        "tagId": str(fake_order_id),
        "tagID": str(fake_order_id),
        "text": "Redacted",
        "timeCreated": FAKE_ISO_TIMESTAMP,
        "timestamp": FAKE_ISO_TIMESTAMP,
        "toAmount": 800.0,
        "tranAmount": 1000,
        "tranWhen": str(fake.date_time_this_decade()),
        "unrealizedDayPL": 1.0,
        "unrealizedDayPLPercent": 1.0,
        "unrealizedPL": 1.0,
        "unrealizedPLPercent": 1.0,
        "userId": FAKE_USER_ID,
        "userID": FAKE_USER_ID,
        "username": fake.simple_profile()["username"],
        "watchlistId": str(fake_order_id),
        "wlpFinTranTypeID": str(fake_order_id),
    }

    return fake, fake_order_id, obfuscated_fields


def _coerce_replacement(original, replacement):
    if replacement is None:
        return None
    if isinstance(original, str):
        return str(replacement)
    if isinstance(original, bool):
        return bool(replacement)
    if isinstance(original, int) and not isinstance(original, bool):
        if isinstance(replacement, (int, float)):
            return int(replacement)
        return replacement
    if isinstance(original, float):
        if isinstance(replacement, (int, float)):
            return float(replacement)
        return replacement
    return replacement


def _looks_like_uuid(value: str) -> bool:
    return bool(UUID_PATTERN.match(value))


def _redact_address(address: dict) -> dict:
    fake, _, obfuscated_fields = _scrub_context()
    redacted = {}
    for field, value in address.items():
        if field in ADDRESS_FIELDS:
            if field in {"postalCode", "postcode", "zip"}:
                redacted[field] = fake.postcode()
            elif field == "country":
                redacted[field] = fake.country_code()
            elif field == "state":
                redacted[field] = fake.state_abbr()
            else:
                redacted[field] = fake.street_address()
        elif isinstance(value, dict):
            redacted[field] = _redact_json(value)
        elif field in obfuscated_fields:
            redacted[field] = _coerce_replacement(value, obfuscated_fields[field])
        else:
            redacted[field] = value
    return redacted


def _redact_json(body):
    if body is None:
        return body

    _, fake_order_id, obfuscated_fields = _scrub_context()

    if isinstance(body, list):
        return [_redact_json(item) for item in body]

    if isinstance(body, dict):
        redacted = {}
        for field, value in body.items():
            if field in {"residentialAddress", "postalAddress"} and isinstance(
                value, dict
            ):
                redacted[field] = _redact_address(value)
            elif isinstance(value, list):
                redacted[field] = [_redact_json(item) for item in value]
            elif isinstance(value, dict):
                redacted[field] = _redact_json(value)
            elif field in obfuscated_fields:
                redacted[field] = _coerce_replacement(value, obfuscated_fields[field])
            elif (
                isinstance(value, str)
                and field.endswith(("Id", "ID"))
                and field not in PRESERVE_ID_FIELDS
                and _looks_like_uuid(value)
            ):
                redacted[field] = str(fake_order_id)
            else:
                redacted[field] = value
        return redacted

    return body


def _normalize_body_string(body):
    if body is None:
        return None
    if isinstance(body, bytes):
        return body
    if isinstance(body, str):
        return body.encode("utf-8")
    return None


def _parse_json_body(body):
    if body is None:
        return None

    if isinstance(body, dict):
        if "string" in body:
            raw = _decode_body_string(body["string"])
            if not raw:
                return None
            return json.loads(raw)
        return body

    raw = _decode_body_string(body)
    if not raw:
        return None
    return json.loads(raw)


def _encode_json_body(payload, original_body):
    serialized = json.dumps(payload, separators=(",", ":"))

    if isinstance(original_body, dict):
        if "string" in original_body:
            string_value = original_body["string"]
            if isinstance(string_value, bytes):
                return {"string": serialized.encode("utf-8")}
            return {"string": serialized}
        return payload

    if isinstance(original_body, bytes):
        return serialized.encode("utf-8")
    if isinstance(original_body, str):
        return serialized

    return serialized.encode("utf-8")


def redact_request_body(body):
    if body is None:
        return None

    try:
        payload = _parse_json_body(body)
    except (json.JSONDecodeError, TypeError):
        return body

    if payload is None:
        return body

    return _encode_json_body(_redact_json(payload), body)


def _decode_body_string(body):
    normalized = _normalize_body_string(body)
    if normalized is None:
        return None
    return normalized.decode("utf-8")


def redact_sensitive_data(response):
    body_string = response.get("body", {}).get("string")
    if body_string:
        raw = _decode_body_string(body_string)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = None
        else:
            response["body"]["string"] = bytes(
                json.dumps(_redact_json(payload), separators=(",", ":")),
                "utf-8",
            )

    if response.get("url"):
        response["url"] = _redact_request_uri(response["url"])

    response["headers"] = {}
    return response


def _redact_request_uri(uri: str) -> str:
    _, fake_order_id, obfuscated_fields = _scrub_context()
    fake_reference = obfuscated_fields["reference"]

    parsed = urlparse(uri)
    path = UUID_IN_PATH_PATTERN.sub(str(fake_order_id), parsed.path)
    query = parse_qsl(parsed.query, keep_blank_values=True)

    if query:
        redacted_query = [
            (
                key,
                fake_reference if key in SENSITIVE_QUERY_PARAMS else value,
            )
            for key, value in query
        ]
        query_string = urlencode(redacted_query)
    else:
        query_string = parsed.query

    return urlunparse(parsed._replace(path=path, query=query_string))


def redact_sensitive_request(request):
    if hasattr(request, "uri"):
        if request.uri:
            request.uri = _redact_request_uri(request.uri)
        if request.body is not None:
            request.body = redact_request_body(request.body)
        return request

    uri = request.get("uri")
    if uri:
        request["uri"] = _redact_request_uri(uri)

    body = request.get("body")
    if body is not None:
        request["body"] = redact_request_body(body)

    return request
