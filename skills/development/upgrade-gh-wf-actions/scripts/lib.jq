# lib.jq — helpers shared by check-updates.sh and release-notes.sh.
# Load with: jq -L "<scripts dir>" 'include "lib"; ...'

# ISO-8601 timestamp (Z or ±hh:mm offset, optional fraction) -> epoch seconds, null if unparsable.
def ts:
  if . == null then null else
    (try (capture("^(?<d>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})(\\.[0-9]+)?(?<z>Z|(?<sg>[+-])(?<h>[0-9]{2}):?(?<m>[0-9]{2}))$")
          | ((.d + "Z") | fromdateiso8601)
            - (if .z == "Z" then 0
               else (if .sg == "+" then 1 else -1 end) * ((.h|tonumber) * 3600 + (.m|tonumber) * 60) end))
     catch null)
  end;

# "v1.2.3" -> {parts:[1,2,3], full:true}; "v1" -> {parts:[1], full:false};
# null for anything that is not v?X(.Y(.Z)) — pre-release suffixes included.
def semver:
  (try capture("^v?(?<a>[0-9]+)(\\.(?<b>[0-9]+))?(\\.(?<c>[0-9]+))?$") catch null)
  | if . == null then null
    else [.a, .b, .c] | map(select(. != null) | tonumber) | {parts: ., full: (length == 3)} end;

def pad3: . + [0, 0, 0] | .[0:3];

# Lines of a release body that match $re (case-insensitive), trimmed and cut to 200 chars.
def matching_lines($re):
  (. // "") | split("\n") | map(gsub("\r"; "") | gsub("^[\\s>*#-]+|\\s+$"; ""))
  | map(select(length > 0 and test($re; "i")))
  | map(if length > 200 then .[0:197] + "..." else . end);
