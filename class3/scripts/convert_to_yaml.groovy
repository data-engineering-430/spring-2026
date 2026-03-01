/*
 * ExecuteScript processor script (Groovy)
 *
 * Reads a JSON FlowFile and converts it to YAML format.
 * Used because NiFi does not include a built-in YAML record writer.
 *
 * Processor configuration:
 *   Script Engine: Groovy
 *   Script Body:   (paste this entire file)
 */

import org.apache.commons.io.IOUtils
import groovy.json.JsonSlurper
import java.nio.charset.StandardCharsets

def flowFile = session.get()
if (!flowFile) return

flowFile = session.write(flowFile, { inputStream, outputStream ->
    def content = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
    def records = new JsonSlurper().parseText(content)

    def sb = new StringBuilder()

    records.each { record ->
        sb.append("- student_id: ${record.student_id}\n")
        sb.append("  first_name: ${record.first_name}\n")
        sb.append("  last_name: ${record.last_name}\n")
        sb.append("  email: ${record.email}\n")
        sb.append("  date_of_birth: '${record.date_of_birth}'\n")
        sb.append("  major: ${record.major}\n")
        sb.append("  gpa: ${record.gpa}\n")
        sb.append("  enrollment_year: ${record.enrollment_year}\n")
        sb.append("  phone_number: ${record.phone_number}\n")
        sb.append("  address: ${record.address}\n")
        sb.append("  city: ${record.city}\n")
        sb.append("  state: ${record.state}\n")
        sb.append("  zip_code: '${record.zip_code}'\n")
    }

    outputStream.write(sb.toString().getBytes(StandardCharsets.UTF_8))
} as org.apache.nifi.processor.io.StreamCallback)

flowFile = session.putAttribute(flowFile, 'filename', 'midwest_students.yaml')
flowFile = session.putAttribute(flowFile, 'mime.type', 'application/x-yaml')
session.transfer(flowFile, REL_SUCCESS)
