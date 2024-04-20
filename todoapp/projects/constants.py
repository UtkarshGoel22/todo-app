MIN_LENGTH = 1
MAX_LENGTH = 10
MAX_ASSOCIATED_PROJECTS = 2
NO_SPACE_LEFT = 0

ERROR_MESSAGES = {
    'ALREADY_MEMBER_OF_PROJECT': 'User is already a member',
    'MAX_ASSOCIATED_PROJECTS_LIMIT': 'Cannot add as user is already a member in two projects',
    'INVALID_USER_IDS': 'Invalid ids present',
    'NOT_A_MEMBER_OF_PROJECT': 'User is not a member of the project',
    'PROJECT_MEMBERS_MAX_LIMIT_REACHED': 'Max limit reached for project members.'
        + ' {remaining_members} members can be added.',
}

SUCCESS_MESSAGES = {
    'MEMBER_ADDED_SUCCESSFULLY': 'Member added successfully',
    'MEMBER_REMOVED_SUCCESSFULLY': 'Member removed successfully',
}
