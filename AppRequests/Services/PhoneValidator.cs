namespace AppRequests.Services
{
    public static class PhoneValidator
    {
        public static bool TryNormalize(string input, out string normalized)
        {
            normalized = null;

            if (string.IsNullOrEmpty(input))
                return false;

            string digits = string.Empty;
            foreach (char c in input)
            {
                if (char.IsDigit(c))
                    digits += c;
            }

            if (digits.Length != 11)
                return false;

            if (digits[0] != '7' && digits[0] != '8')
                return false;

            normalized = '7' + digits.Substring(1);
            return true;
        }
    }
}
