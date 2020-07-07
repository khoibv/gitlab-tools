import gitlab
import csv
import sys

if len(sys.argv) != 4:
    print('Usage:')
    print('  python collect-comments.py <gitlab url> <project name> <access token>')
    print('For example:')
    print('  python collect-comments.py http://172.20.108.250 ngc xxxxxxxxxxxxxxxxxxxx')

print(sys.argv)

GITLAB_SERVER = sys.argv[1]  # 'http://172.20.108.250'
PROJECT_NAME = sys.argv[2]  # 'ngc'
ACCESS_TOKEN = sys.argv[3]  # 'xxxxxxxxxxxxxxxxxxxx'
OUTPUT_CSV_FILE = PROJECT_NAME + '.csv'

# private token or personal token authentication
gl = gitlab.Gitlab(GITLAB_SERVER, ACCESS_TOKEN)

# make an API request to create the gl.user object. This is mandatory if you
# use the username/password authentication.
gl.auth()

projects = gl.projects.list()

targetProject = None
for project in projects:
    if project.name == PROJECT_NAME:
        targetProject = project

if targetProject is None:
    raise Exception('Project {} is not exists in {}'.format(PROJECT_NAME, GITLAB_SERVER))

mergeRequestPageIndex = 1
mergeRequestPageLength = 100
mergeRequestList = targetProject.mergerequests.list(page=mergeRequestPageIndex, per_page=mergeRequestPageLength)

with open(OUTPUT_CSV_FILE, newline='', mode='w', encoding='utf-8') as csv_file:
    comment_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    fieldnames = [
        'merge_request_id',
        'merge_request_title',
        'merge_request_author',
        'merge_state',
        'merge_created_at',
        'merge_updated_at',
        'merge_from',
        'merge_to',
        'merge_url',
        'comment',
        'comment_by',
        'comment_created_at',
        'comment_updated_at',
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write header lines
    writer.writeheader()

    while len(mergeRequestList) > 0:
        for mr in mergeRequestList:
            # Write content
            print(mr.id, mr.iid)
            if mr.user_notes_count > 0:
                for note in mr.notes.list():
                    if not note.system:
                        writer.writerow(
                            {
                                'merge_request_id': mr.iid,
                                'merge_request_title': mr.title,
                                'merge_request_author': mr.author.name,
                                'merge_state': mr.state,
                                'merge_created_at': mr.created_at,
                                'merge_updated_at': mr.updated_at,
                                'merge_from': mr.source_branch,
                                'merge_to': mr.target_branch,
                                'merge_url': mr.web_url,
                                'comment': note.body,
                                'comment_by': note.author.name,
                                'comment_created_at': note.created_at,
                                'comment_updated_at': note.updated_at,
                            })

        # Fetch next merge requests
        mergeRequestPageIndex = mergeRequestPageIndex + 1
        mergeRequestList = targetProject.mergerequests.list(page=mergeRequestPageIndex,
                                                            per_page=mergeRequestPageLength)
