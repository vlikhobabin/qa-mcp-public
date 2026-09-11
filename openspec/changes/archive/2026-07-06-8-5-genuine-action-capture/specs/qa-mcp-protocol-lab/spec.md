## ADDED Requirements

### Requirement: The genuine-action capture pipeline is proven on the 8.5 contour
The protocol lab SHALL establish, on the 8.5 contour, a genuine-action capture
pipeline that drives one action against the `lTestClient` fixture form, records a
clean packet capture of the client↔manager traffic, and converts it to a
`traffic.jsonl` in the same format the 8.3 corpus uses. The chosen capture path
(Vanessa TestManager on 8.5 vs the native `tcpdump`-on-`lo` driver) SHALL be
recorded so P2 can scale the same path to the full corpus.

#### Scenario: One genuine 8.5 action is captured and converted
- **WHEN** the `lTestClient` fixture form is opened on the 8.5 TestClient and a
  single genuine action is driven against it while the client↔manager traffic on
  the loopback TPort is captured
- **THEN** a clean pcap of that action is produced and `pcap_to_traffic.py`
  converts it to a `traffic.jsonl` whose manager/client frames parse in the
  existing capture format
- **AND** the rendered fixture form and the sample `traffic.jsonl` are retained as
  evidence

#### Scenario: The 8.5 capture path is determined and recorded
- **WHEN** the capture path is established on 8.5
- **THEN** it is recorded whether the Vanessa TestManager runs on 8.5 (reusing the
  genuine-action recipe) or the native `tcpdump`-on-`lo` driver path is required
- **AND** the recorded path is the one P2 uses to re-capture the full corpus
  (handshake + frame templates + the action/foreground captures)
