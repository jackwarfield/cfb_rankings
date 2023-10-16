#include <cmath>
#include <vector>

namespace glicko2 {

double g(double phi) {
  return 1.0 / sqrt(1.0 + 3.0 * phi * phi / (M_PI * M_PI));
}

double Ej(double mu, double muj, double phij) {
  return 1.0 / (1.0 + exp(-g(phij) * (mu - muj)));
}

double v(double mu, double muj, double phij) {
  double E_val = Ej(mu, muj, phij);
  return 1.0 / (pow(g(phij), 2.0) * E_val * (1 - E_val));
}

double f(double x, double delta, double phi, double vi, double a, double tau) {
  double topl = exp(x) * (delta * delta - phi * phi - vi - exp(x));
  double botl = 2 * pow(phi * phi + vi + exp(x), 2.0);
  double right = (x - a) / (tau * tau);
  return (topl / botl - right);
}

double iterSigPr(double sig, double delta, double phi, double vi, double tau,
                 double eps = 1e-8) {
  double a = log(sig * sig);
  double A = a;
  double B;
  if (delta * delta > phi * phi + vi) {
    B = log(delta * delta - phi * phi - vi);
  } else {
    double k = 1;
    while (f(a - k * tau, delta, phi, vi, a, tau) < 0) {
      k++;
    }
    B = a - k * tau;
  }
  double fA = f(A, delta, phi, vi, a, tau);
  double fB = f(B, delta, phi, vi, a, tau);
  double C;
  double fC;
  while (std::abs(B - A) > eps) {
    C = A + (A - B) * fA / (fB - fA);
    fC = f(C, delta, phi, vi, a, tau);
    if (fC * fB <= 0) {
      A = B;
      fA = fB;
    } else {
      fA = fA / 2.0;
    }
    B = C;
    fB = fC;
  }
  return exp(A / 2.0);
}

std::vector<double> update_ratings(double r1, double rd1, double sig1,
                                   double r2, double rd2, double sig2,
                                   bool t1win) {
  double tau = 0.2;

  double mu1 = (r1 - 1500) / 173.7178;
  double phi1 = rd1 / 173.7178;
  double mu2 = (r2 - 1500) / 173.7178;
  double phi2 = rd2 / 173.7178;

  double v1 = v(mu1, mu2, phi2);
  double v2 = v(mu2, mu1, phi1);

  double s1, s2;
  if (t1win) {
    s1 = 1, s2 = 0;
  } else {
    s1 = 0, s2 = 1;
  }

  double delta1 = v1 * g(phi2) * (s1 - Ej(mu1, mu2, phi2));
  double delta2 = v2 * g(phi1) * (s2 - Ej(mu2, mu1, phi1));

  double sigPr1 = iterSigPr(sig1, delta1, phi1, v1, tau);
  double sigPr2 = iterSigPr(sig2, delta2, phi2, v2, tau);

  double phiStar1 = sqrt(phi1 * phi1 + sigPr1 * sigPr1);
  double phiStar2 = sqrt(phi2 * phi2 + sigPr2 * sigPr2);

  double phiPr1 = 1.0 / sqrt(1.0 / (phiStar1 * phiStar1) + 1.0 / v1);
  double phiPr2 = 1.0 / sqrt(1.0 / (phiStar2 * phiStar2) + 1.0 / v2);

  double muPr1 = mu1 + phiPr1 * phiPr1 * g(phi2) * (s1 - Ej(mu1, mu2, phi2));
  double muPr2 = mu2 + phiPr2 * phiPr2 * g(phi1) * (s2 - Ej(mu2, mu1, phi1));

  double rPr1 = 173.7178 * muPr1 + 1500.0;
  double rdPr1 = 173.7178 * phiPr1;
  double rPr2 = 173.7178 * muPr2 + 1500.0;
  double rdPr2 = 173.7178 * phiPr2;

  std::vector<double> results{rPr1, rdPr1, sigPr1, rPr2, rdPr2, sigPr2};
  return results;
}

} // namespace glicko2
