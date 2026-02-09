package totp

import (
	"crypto/rand"
	"encoding/base32"
	"net/url"
	"time"

	"github.com/pquerna/otp"
	"github.com/pquerna/otp/totp"
)

// GenerateSecret generates a new TOTP secret
func GenerateSecret() (string, error) {
	key, err := totp.Generate(totp.GenerateOpts{
		Issuer:      "AreaX Control Plane",
		AccountName: "user@example.com",
		Period:      30,
		SecretSize:  32,
		Digits:      otp.DigitsSix,
		Algorithm:   otp.AlgorithmSHA1,
	})
	if err != nil {
		return "", err
	}
	return key.Secret(), nil
}

// GenerateQRCodeURL generates a QR code URL for the TOTP setup
func GenerateQRCodeURL(accountName, issuer, secret string) string {
	u := url.URL{}
	u.Scheme = "otpauth"
	u.Host = "totp"
	u.Path = "/" + issuer + ":" + accountName
	
	q := u.Query()
	q.Set("secret", secret)
	q.Set("issuer", issuer)
	u.RawQuery = q.Encode()
	
	return u.String()
}

// ValidateCode validates a TOTP code against a secret
func ValidateCode(code, secret string) (bool, error) {
	valid := totp.Validate(code, secret)
	return valid, nil
}

// GenerateCode generates a TOTP code for the given time (for testing)
func GenerateCode(secret string, t time.Time) (string, error) {
	code, err := totp.GenerateCode(secret, t)
	if err != nil {
		return "", err
	}
	return code, nil
}

// GenerateRecoveryCodes generates a list of recovery codes
func GenerateRecoveryCodes(count int) ([]string, error) {
	codes := make([]string, count)
	for i := 0; i < count; i++ {
		code, err := generateRandomCode(10)
		if err != nil {
			return nil, err
		}
		codes[i] = code
	}
	return codes, nil
}

func generateRandomCode(length int) (string, error) {
	bytes := make([]byte, length)
	_, err := rand.Read(bytes)
	if err != nil {
		return "", err
	}
	// Convert to base32 and take first 'length' characters
	encoded := base32.StdEncoding.EncodeToString(bytes)
	if len(encoded) > length {
		encoded = encoded[:length]
	}
	return encoded, nil
}

// GenerateNumericCode generates a numeric recovery code
func GenerateNumericCode(length int) (string, error) {
	const digits = "0123456789"
	result := make([]byte, length)
	for i := 0; i < length; i++ {
		b := make([]byte, 1)
		if _, err := rand.Read(b); err != nil {
			return "", err
		}
		result[i] = digits[b[0]%byte(len(digits))]
	}
	return string(result), nil
}
