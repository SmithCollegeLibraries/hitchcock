Feature: Video

  Scenario: Ingest, playing, access, publishing
    Given I am logged in as a staff user
      When I ingest a video object
      And I go to the current object URL
      Then a working video player should load
    Given I am a non-staff user
      When I go to the video
      Then I am forbidden
    Given I am logged in as a staff user
      When I set the video as published
    Given I am a non-staff user
      When I go to the video
      Then a working video player should load
