def initial_story_points_from(epic):
    """Story point estimate initially set on an epic"""

    return epic.fields.customfield_10026


def story_points_from(story):
    """Story point estimate set on an story"""

    return story.fields.customfield_10026
