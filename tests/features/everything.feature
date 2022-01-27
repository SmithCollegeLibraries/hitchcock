Feature: Everything

  Scenario Outline: AV Objects ingest, playing, publishing, searching
    Given I am logged in as a staff user
      When I ingest an object of type "<object_type>"
      Then a valid object view URL should be displayed
      When I go to the current "<object_type>" object view URL
      Then a working "<asset_viewer>" should load
      # When I search for the title of the "<object_type>" object with inverse case
      # The item should appear in the search results
    # Given I am logged in as a staff user
      # When I create a playlist of type "<playlist_type>"
      # Then a valid playlist URL should be displayed
      # When I go to the current "<playlist_type>" view URL
      # Then a playlist with the correct name and number of items should be displayed
    Given I am logged in as a staff user
      When I set the "<object_type>" as "un-published"
    Given I am a non-staff user
      When I go to the "<object_type>"
      Then I am forbidden
    Given I am logged in as a staff user
      When I set the "<object_type>" as "published"
    Given I am a non-staff user
      When I go to the "<object_type>"
      Then a working "<asset_viewer>" should load

  Examples: Objects
    | object_type    | asset_viewer |
    | text           | pdf viewer   |
    | video          | av player    |
    | audio          | av player    |
