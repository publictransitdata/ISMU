include("$(PORT_DIR)/boards/manifest.py")

package("app", opt=2)
package("utils", opt=2)

module("font.py", base_path="lib", opt=2)
module("lang.py", base_path="lib", opt=2)
module("microdot.py", base_path="lib", opt=2)
module("sh1106.py", base_path="lib", opt=2)
module("writer.py", base_path="lib", opt=2)
