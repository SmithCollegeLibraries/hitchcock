Feature: Everything

  Scenario: Video ingest, playing, access, publishing
    Given I am logged in as a staff user
      When I ingest a video object
      And I go to the current video object URL
      Then a working AV player should load
    Given I am a non-staff user
      When I go to the video
      Then I am forbidden
    Given I am logged in as a staff user
      When I set the video as published
    Given I am a non-staff user
      When I go to the video
      Then a working AV player should load

  Scenario: Audio ingest, playing, access, publishing
    Given I am logged in as a staff user
      When I ingest a audio object
      And I go to the current audio object URL
      Then a working AV player should load
    Given I am a non-staff user
      When I go to the audio
      Then I am forbidden
    Given I am logged in as a staff user
      When I set the audio as published
    Given I am a non-staff user
      When I go to the audio
      Then a working AV player should load

  Scenario: Text ingest, playing
    Given I am logged in as a staff user
      When I ingest a text object
      And I go to the current text object URL
      Then a working PDF viewer should load

  @wip
  Scenario: Audio album ingest, playing, access, publishing
    Given I am logged in as a staff user
      When I ingest a "audio album" object
      And I go to the current "audio album" object URL
      Then a working AV player should load
    Given I am a non-staff user
      When I go to the "audio album"
      Then I am forbidden
    Given I am logged in as a staff user
      When I set the "audio album" as published
    Given I am a non-staff user
      When I go to the "audio album"
      Then a working AV player should load
