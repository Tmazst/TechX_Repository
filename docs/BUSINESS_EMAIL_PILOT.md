# Business Email pilot

Customers choose Business Email in Services, then choose a TechX subdomain or an existing domain. My Email shows their own requests and the next action.

- A new eswtn.com request also appears in the Domain Admin subdomain queue. Approve it there first. The email request can also use an active TechX subdomain the customer already owns.
- For a customer-owned domain, the customer adds the TXT record shown in My Email and selects Check DNS. Email approval rechecks the record.
- In Domain Admin → Email requests, approve the mailbox and create it on the mail server. Verify whether it already exists before provisioning an address. The application reserves approved addresses.
- Select Confirm mailbox created. The customer-owned path then displays MX and SPF guidance. Confirm the customer’s cutover timing and DKIM/DMARC values separately. For a TechX subdomain, staff publish the agreed records through Cloudflare.
- Test IMAP mailbox login and send and receive with an external mailbox, then mark the request ready. The portal also checks that the domain's published MX targets point only to mail.eswtn.com. Give the customer the mailbox credentials through the approved private channel.
- When [Webmail](WEBMAIL.md) is enabled, customers can open it from Business Email and from ready mailboxes in My Email.

This release tracks requests and DNS checks. It does not modify Postfix or Dovecot, issue credentials, publish DNS records, or migrate existing mail. It requires the existing dnspython dependency. Back up the app database before deploying. On first use, the app creates the business_email_request table.
