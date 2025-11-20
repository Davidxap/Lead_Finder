# Changelog

## [Unreleased]

### Fixed

- **API Interaction**: Fixed `_build_request_body` in `linkedin_api.py` to correctly prioritize `location` and send only one filter to the external API, resolving 500 errors.
- **Local Filtering**: Implemented robust client-side filtering in `linkedin_api.py` for `title`, `company`, `region`, and other fields to compensate for API limitations.
- **Zero Results**: Renamed `_parse_lead` to `parse_lead_data` in `linkedin_api.py` to fix `AttributeError` preventing leads from being displayed.
- **Template Corruption**: Restored corrupted `leads/templates/leads/search.html` and `leads/views.py`, fixing `TemplateSyntaxError` and `IndentationError`.
- **Data Persistence**: Verified and ensured all lead data (email, phone, etc.) is correctly passed from the search results to the "Add to List" modal and saved to the database.
- **UI Enhancements**:
  - Added an "Email" column with `mailto:` links to the search results table.
  - Updated "My Lists" view to display the email address text explicitly.

### Added

- **Logging**: Added detailed logging to `linkedin_api.py` and `views.py` to trace API requests, responses, local filtering counts, and form data for debugging.
