## ADDED Requirements

### Requirement: An 8.5 platform lab contour exists for protocol re-capture
The protocol lab SHALL provide a repeatable **8.5 platform contour** — a fixture
infobase that carries the `lTestClient` fixture plus a documented headless
TestClient boot — so genuine 8.5 wire traffic can be captured without disturbing
the 8.3 contour. The 8.5 fixture infobase SHALL be a one-time-converted *copy* of
the 8.3 `vanessa_client` file infobase, leaving the original 8.3 infobase and its
Apache OData publication untouched.

#### Scenario: An 8.5 TestClient boots against the converted fixture infobase
- **WHEN** the 8.5 platform (`PLATFORM_ROOT` = `…/8.5.x.y`) opens the converted
  fixture infobase under Xvfb in `/TESTCLIENT` mode
- **THEN** the client authenticates as the fixture admin user, the database has
  been one-time-converted to the 8.5 format, and the client listens on its TPort
  with a valid (developer) license and no fatal startup error
- **AND** a retained screenshot evidences the rendered managed UI of the fixture
  configuration on 8.5

#### Scenario: The 8.5 contour does not disturb the 8.3 contour
- **WHEN** the 8.5 lab infobase is created
- **THEN** it is a copy at a separate filesystem path; the original 8.3
  `vanessa_client` infobase and the Apache OData publication bound to it are not
  modified and need not be stopped (the copy is a distinct file → no file-infobase
  version contention)
- **AND** the 8.5 lab-boot recipe is documented for repeatable capture runs as an
  8.5 analogue of the native-TestClient-under-Xvfb procedure
