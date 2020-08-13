Feature: Everything

  Scenario Outline: AV Objects ingest, playing, publishing
    Given I am logged in as a staff user
      When I ingest a "<object_type>" object
      And I go to the current "<object_type>" object URL
      Then a working "<asset_viewer>" should load
    Given I am a non-staff user
      When I go to the "<object_type>"
      Then I am forbidden
    Given I am logged in as a staff user
      When I set the "<object_type>" as published
    Given I am a non-staff user
      When I go to the "<object_type>"
      Then a working "<asset_viewer>" should load

  Examples: Objects
    | object_type | asset_viewer  |
    | video       | av player     |
    | audio       | av player     |
    | audio album | av player     |
    | text        | pdf viewer    |
