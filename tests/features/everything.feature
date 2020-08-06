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

  @wip
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
